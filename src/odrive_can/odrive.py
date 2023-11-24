#!/usr/bin/env python3
"""
 ODrive CAN driver

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging
import threading
from enum import Enum
from typing import Callable, Optional

import can

from odrive_can import extract_ids, get_dbc
from odrive_can.interface import DbcInterface
from odrive_can.timer import Timer

# message timeout in seconds
MESSAGE_TIMEOUT = 0.2
CUSTOM_TIMEOUTS = {"Heartbeat": 0.5}


dbc = get_dbc()


class DriveError(Exception):
    """ODrive drive error"""


class HeartbeatError(Exception):
    """No heartbeat error"""


class CommandId(Enum):
    """short list of command IDs, used for ignoring messages"""

    HEARTBEAT = 0x01
    ENCODER_ESTIMATE = 0x09


class CanMsg:
    """class to manage CAN messages"""

    def __init__(self, msg: can.Message):
        db_msg = dbc.get_message_by_frame_id(msg.arbitration_id)
        self.name = db_msg.name.split("_", 1)[1]  # remove "AxisX_" prefix
        self.data = db_msg.decode(msg.data)

        timeout = CUSTOM_TIMEOUTS.get(self.name, MESSAGE_TIMEOUT)

        self._timer = Timer(timeout=timeout)

    def is_expired(self):
        """check if timer has expired"""
        return self._timer.is_timeout()

    def __str__(self):
        return f"{self.name}: {self.data}"


class ODriveCAN(DbcInterface):
    """odrive CAN driver"""

    def __init__(
        self,
        axis_id: int = 0,
        interface: str = "can0",
        interface_type: str = "socketcan",
    ):
        self._log = logging.getLogger(f"odrive.{axis_id}")
        self._log.info(f"Starting mock {axis_id=} , {interface=} , {interface_type=}")
        self._axis_id = axis_id

        self._bus = can.interface.Bus(channel=interface, interface=interface_type)
        # self._notifier = can.Notifier(self._bus, [self._message_handler])

        self._recieve_thread: Optional[threading.Thread] = None
        self._msg_queue: asyncio.Queue = asyncio.Queue()

        self._messages: dict[str, CanMsg] = {}  # latest message for each type

        self._ignored_messages: set = set()  # message ids to ignore

        self._response_event = asyncio.Event()  # event to signal response to rtr
        self._request_id: int = 0  # request id for rtr

        # called on incoming position message
        self.position_callback: Optional[Callable] = None

        self._running = True  # flag to stop loops

    def check_alive(self):
        """check if axis is alive, rasie an exception if not"""
        if "Heartbeat" not in self._messages:
            raise HeartbeatError("Error: No heartbeat message received.")

        if self._messages["Heartbeat"].is_expired():
            raise HeartbeatError("Error: Heartbeat message timeout.")

    def check_errors(self):
        """Check if axis is in error and raise an exception if so."""
        if "Heartbeat" not in self._messages:
            raise HeartbeatError("Error: No heartbeat message received.")

        msg = self._messages["Heartbeat"]

        if msg.data["Axis_Error"] != "NONE":
            raise DriveError(f"Axis Error: {msg.data['Axis_Error']}")

        for field in [
            "Motor_Error_Flag",
            "Encoder_Error_Flag",
            "Controller_Error_Flag",
        ]:
            if msg.data[field] != 0:
                raise DriveError(f"{field} Error Detected")

    def ignore_message(self, cmd_id: CommandId):
        """ignore message by command ID"""
        self._ignored_messages.add(cmd_id.value)

    def allow_message(self, cmd_id: CommandId):
        """allow message by command ID"""
        self._ignored_messages.remove(cmd_id.value)

    @property
    def axis_state(self) -> str:
        """get axis state"""
        return self._messages["Heartbeat"].data["Axis_State"]

    async def start(self):
        """start driver"""
        self._log.info("starting driver")
        loop = asyncio.get_running_loop()  # Get the current asyncio event loop
        self._recieve_thread = threading.Thread(
            target=self._can_reader_thread, args=(loop,), daemon=True
        )
        self._recieve_thread.start()

        asyncio.create_task(self._message_handler())
        await asyncio.sleep(0.5)  # wait for first heartbeat

    def stop(self):
        """stop driver"""
        self._log.info("stopping driver")
        self.set_axis_state("IDLE")

        self._running = False

        self._recieve_thread.join()

    # ------------------- private -------------------
    async def _request(self, msg_name: str, timeout: float = 0.5) -> dict:
        """Send an RTR message and wait for the response with a timeout."""

        # check if another request is in progress
        if self._response_event.is_set():
            raise RuntimeError("another request is already in progress")

        # self._response_event.clear()  # Reset the event before waiting

        # Send the request
        self._send_message(msg_name, rtr=True)

        self._log.debug(f"{self._response_event.is_set()=} {self._request_id=}")

        try:
            # Wait for the response with a timeout
            await asyncio.wait_for(self._response_event.wait(), timeout)
            self._log.debug("awaited response")
        except asyncio.TimeoutError as error:
            # Handle the timeout
            self._log.error(f"Timeout waiting for response to {msg_name}")
            raise TimeoutError(f"Timeout waiting for response to {msg_name}") from error

        self._clear_request()

        # Process and return the response
        response = self._messages.get(msg_name)
        return response.data if response else {}

    def _clear_request(self):
        """clear request"""
        self._log.debug("clearing request")
        self._response_event.clear()
        self._request_id = 0

    def _send_message(
        self, msg_name: str, msg_dict: Optional[dict] = None, rtr: bool = False
    ):
        """send message by name. If no msg_dict is provided, use zeros
        msg_name is the name of the message without the "AxisX_" prefix
        """
        msg = dbc.get_message_by_name(f"Axis{self._axis_id}_{msg_name}")
        if rtr:
            # For RTR messages, don't specify the data field
            msg = can.Message(
                arbitration_id=msg.frame_id,
                is_extended_id=False,
                is_remote_frame=True,
            )
            # set request id for response
            self._request_id = msg.arbitration_id
        else:
            full_msg_dict = {signal.name: 0 for signal in msg.signals}
            if msg_dict is not None:
                full_msg_dict.update(msg_dict)

            data = msg.encode(full_msg_dict)
            msg = can.Message(
                arbitration_id=msg.frame_id,
                data=data,
                is_extended_id=False,
            )
        try:
            self._bus.send(msg)  # type: ignore
        except can.CanError as error:
            self._log.error(error)

    def __del__(self):
        """destructor"""
        self._bus.shutdown()

    def _can_reader_thread(self, loop):
        """receive can messages, filter and put them into the queue"""
        while self._running:
            try:
                msg = self._bus.recv(MESSAGE_TIMEOUT)
                if not msg:
                    self._log.warning("can timeout")
                    continue

                axis_id, cmd_id = extract_ids(msg.arbitration_id)

                # Ignore messages that aren't for this axis
                if axis_id != self._axis_id:
                    continue

                # Ignore messages that were requested to be ignored, this is used
                # to increase performance especially for frequent encoder updates
                if cmd_id in self._ignored_messages:
                    continue

                # RTR messages are requests for data, they don't have a data payload
                # no RTR messages are sent by the odrive, this should not happen
                if msg.is_remote_frame:
                    self._log.warning("RTR message received")
                    continue

                self._log.debug(f"< {axis_id=} {cmd_id=}")

                asyncio.run_coroutine_threadsafe(
                    self._msg_queue.put((cmd_id, msg)), loop
                )
            except Exception as e:  # pylint: disable=broad-except
                self._log.error(f"Error in CAN reader thread: {e}")

        self._log.debug("CAN reader thread stopped")

    async def _message_handler(self):
        """handle received message"""

        while self._running:
            cmd_id, msg = await self._msg_queue.get()
            self._msg_queue.task_done()
            try:
                # process message
                can_msg = CanMsg(msg)
                self._messages[can_msg.name] = can_msg

                # check if this is a response to a request
                if msg.arbitration_id == self._request_id:
                    self._log.debug("response received")
                    self._response_event.set()

                # call position callback
                if cmd_id == CommandId.ENCODER_ESTIMATE.value:
                    if self.position_callback is not None:
                        self.position_callback(can_msg.data)

                # debug heartbeat
                if cmd_id == CommandId.HEARTBEAT.value:
                    self._log.debug(f"heartbeat: {can_msg.data}")

            except KeyError:
                # If the message ID is not in the DBC file, print the raw message
                self._log.info(f"Raw: {msg}")

        self._log.debug("message handler stopped")
