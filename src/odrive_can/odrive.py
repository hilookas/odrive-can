#!/usr/bin/env python3
"""
 ODrive CAN driver

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""


# import asyncio
import logging
from typing import Optional

import can

from odrive_can.timer import Timer
from odrive_can import get_dbc, get_axis_id

MESSAGE_TIMEOUT = 0.1  # seconds
CUSTOM_TIMEOUTS = {"Heartbeat": 1.1}


dbc = get_dbc()


class DriveError(Exception):
    """ODrive drive error"""


class HeartbeatError(Exception):
    """No heartbeat error"""


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


class ODriveCAN:
    """odrive CAN driver"""

    def __init__(
        self, axis_id: int = 0, channel: str = "can0", interface: str = "socketcan"
    ):
        self._log = logging.getLogger(f"odrive.{axis_id}")
        self._log.info(f"Starting mock {axis_id=} , {channel=} , {interface=}")
        self._axis_id = axis_id

        self._bus = can.interface.Bus(channel=channel, interface=interface)
        self._notifier = can.Notifier(self._bus, [self._message_handler])

        self._messages: dict[str, CanMsg] = {}  # latest message for each type

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

    def _message_handler(self, msg: can.Message):
        """handle received message"""

        if get_axis_id(msg) != self._axis_id:
            # Ignore messages that aren't for this axis
            return

        if msg.is_remote_frame:
            # RTR messages are requests for data, they don't have a data payload
            # no RTR messages are sent by the odrive, this should not happen
            self._log.warning("RTR message received")
            return

        try:
            # process message
            can_msg = CanMsg(msg)
            self._log.debug(f"received {can_msg.name}: {can_msg.data}")
            self._messages[can_msg.name] = can_msg

        except KeyError:
            # If the message ID is not in the DBC file, print the raw message
            self._log.info(f"Raw: {msg}")

    def _send_message(
        self, msg_name: str, msg_dict: Optional[dict] = None, rtr: bool = False
    ):
        """send message by name. If no msg_dict is provided, use zeros"""
        msg = dbc.get_message_by_name(msg_name)
        if rtr:
            # For RTR messages, don't specify the data field
            msg = can.Message(
                arbitration_id=msg.frame_id,
                is_extended_id=False,
                is_remote_frame=True,
            )
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

        self._bus.send(msg)  # type: ignore

    def __del__(self):
        """destructor"""
        self._notifier.stop()
        self._bus.shutdown()
