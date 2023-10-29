#!/usr/bin/env python3
"""
 mock ODrive CAN interface

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging

import can
import coloredlogs

from odrive_can import LOG_FORMAT, TIME_FORMAT, get_dbc

# pylint: disable=abstract-class-instantiated


class ODriveCANMock:
    """class to mock ODrive CAN interface"""

    def __init__(
        self, axis_id: int = 0, channel: str = "vcan0", bustype: str = "socketcan"
    ):
        self.dbc = get_dbc()
        self.axis_id = axis_id

        self.bus: can.interface.Bus = can.interface.Bus(
            channel=channel, bustype=bustype
        )

    async def heartbeat_loop(self, delay: float = 1.0):
        """send heartbeat message"""
        logging.info("Starting heartbeat loop")

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

    async def encoder_loop(self, delay: float = 0.5):
        """send encoder message"""
        logging.info("Starting encoder loop")
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
        await asyncio.gather(self.heartbeat_loop(), self.encoder_loop())

    def start(self):
        """start the main loop"""
        asyncio.run(self.main())

    def __del__(self):
        self.bus.shutdown()


def main():
    logging.info("Starting ODrive CAN mock")

    mock = ODriveCANMock()
    mock.start()


if __name__ == "__main__":
    coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped")
