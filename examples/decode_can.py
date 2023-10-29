#!/usr/bin/env python3
"""
 inspect and decode CAN messages for ODrive

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import can
import odrive_can

# pylint: disable=abstract-class-instantiated


def receive_and_decode(bus, dbc):
    while True:
        message = bus.recv()
        try:
            # Attempt to decode the message using the DBC file
            decoded_message = dbc.decode_message(message.arbitration_id, message.data)
            print(f"Received Message: {decoded_message}")
        except KeyError:
            # If the message ID is not in the DBC file, print the raw message
            print(f"Received Raw Message: {message}")


def main():
    # Load the DBC file
    dbc = odrive_can.get_dbc()

    channel = "vcan0"  # Change to your CAN interface
    bus = can.Bus(channel=channel, bustype="socketcan", receive_own_messages=True)

    try:
        receive_and_decode(bus, dbc)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
