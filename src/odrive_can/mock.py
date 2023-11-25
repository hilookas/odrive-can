#!/usr/bin/env python3
"""
 mock ODrive CAN interface

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import time
import logging
from typing import Optional

import can
import coloredlogs  # type: ignore

from odrive_can import LOG_FORMAT, TIME_FORMAT, get_dbc, get_axis_id
from odrive_can.linear_model import LinearModel

# pylint: disable=abstract-class-instantiated, unnecessary-lambda

log = logging.getLogger("odrive.mock")


class OdriveMock:
    """mock physical ODrive device, excluding CAN interface"""

    def __init__(self):
        self.model = LinearModel(roc=10.0)

        self.axis_state = "AXIS_STATE_UNDEFINED"
        self.input_mode = "INACTIVE"
        self.controller_mode = "VELOCITY_CONTROL"

    def set_axis_state(self, state: str):
        """set axis state"""
        log.info(f"Setting axis state to {state}")
        time.sleep(0.5)
        self.axis_state = state
        log.info(f"Axis state is now {self.axis_state}")


class ODriveCANMock:
    """class to mock ODrive CAN interface"""

    def __init__(
        self, axis_id: int = 0, channel: str = "vcan0", bustype: str = "socketcan"
    ):
        log.info(f"Starting mock {axis_id=} , {channel=} , {bustype=}")
        self.dbc = get_dbc()
        self.axis_id = axis_id

        self.bus = can.interface.Bus(channel=channel, bustype=bustype)
        self.can_reader = can.AsyncBufferedReader()
        self.notifier = can.Notifier(self.bus, [self.can_reader])

        self.odrive = OdriveMock()

        # mapping of commands to functions
        self._cmd_map = {"Set_Axis_State": lambda x: self.odrive.set_axis_state(x)}

    async def message_handler(self):
        """handle received message"""

        log.info("Starting message handler")

        while True:
            try:
                msg = await self.can_reader.get_message()
                log.debug(f"Received: {msg}")

                if get_axis_id(msg) != self.axis_id:
                    # Ignore messages that aren't for this axis
                    continue

                db_msg = self.dbc.get_message_by_frame_id(msg.arbitration_id)

                if msg.is_remote_frame:
                    # RTR messages are requests for data, they don't have a data payload
                    log.info(f"Get: {db_msg.name}")
                    # echo RTR messages back with data
                    self.send_message(db_msg.name)
                    continue

                # decode message data
                data = db_msg.decode(msg.data)
                cmd = db_msg.name.split("_", 1)[1]  # remove "AxisX_" prefix

                log.info(f"Set: {cmd}: {data}")

                # set paramter

            except KeyError:
                # If the message ID is not in the DBC file, print the raw message
                log.warning(f"Could not decode: {msg}")
            except Exception as e:
                log.error(f"Error: {e}")

    def send_message(
        self, msg_name: str, msg_dict: Optional[dict] = None, rtr: bool = False
    ):
        """send message by name. If no msg_dict is provided, use zeros"""
        msg = self.dbc.get_message_by_name(msg_name)
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

        self.bus.send(msg)  # type: ignore

    async def heartbeat_loop(self, delay: float = 0.2):
        """send heartbeat message"""
        log.info("Starting heartbeat loop")

        # Fetch the "Axis0_Heartbeat" message from the DBC database
        heartbeat_msg = self.dbc.get_message_by_name(f"Axis{self.axis_id}_Heartbeat")

        while True:
            # Construct the data payload using the DBC message definition
            data = heartbeat_msg.encode(
                {
                    "Axis_Error": 0,
                    "Axis_State": "IDLE",
                    "Motor_Error_Flag": 0,
                    "Encoder_Error_Flag": 0,
                    "Controller_Error_Flag": 0,
                    "Trajectory_Done_Flag": 0,
                }
            )

            # Send the message
            message = can.Message(
                arbitration_id=heartbeat_msg.frame_id, data=data, is_extended_id=False
            )
            self.bus.send(message)

            await asyncio.sleep(delay)

    async def encoder_loop(self, delay: float = 0.1):
        """send encoder message"""
        log.info("Starting encoder loop")
        position = 0.0
        msg = self.dbc.get_message_by_name(f"Axis{self.axis_id}_Get_Encoder_Estimates")

        while True:
            data = msg.encode({"Pos_Estimate": position, "Vel_Estimate": 0.1})
            message = can.Message(
                arbitration_id=msg.frame_id, data=data, is_extended_id=False
            )
            self.bus.send(message)
            position += 0.01  # Increment position to simulate movement

            await asyncio.sleep(delay)

    async def main(self):
        """main loop"""

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.heartbeat_loop())
            tg.create_task(self.encoder_loop())
            tg.create_task(self.message_handler())

    def start(self):
        """start the main loop"""
        asyncio.run(self.main())

    def __del__(self):
        """destructor"""
        self.notifier.stop()
        self.bus.shutdown()


def main(axis_id: int = 0, interface: str = "vcan0"):
    try:
        mock = ODriveCANMock(axis_id, interface)
        mock.start()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")


if __name__ == "__main__":
    coloredlogs.install(level="DEBUG", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
    main()
