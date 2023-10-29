#!/usr/bin/env python3
"""
 Send some test messages to the drive

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from typing import Optional
from time import sleep
import can
from odrive_can import get_dbc

# pylint: disable=abstract-class-instantiated
BUS = can.interface.Bus(
    channel="vcan0", bustype="socketcan", receive_own_messages=False
)
DB = get_dbc()  # Load the DBC file

IGNORED_MESSAGES = [9]  # List of message IDs to ignore


# Callback function to process received messages
def print_message(msg):
    """print message, if not ignored"""
    if msg.arbitration_id in IGNORED_MESSAGES:
        return

    try:
        # Attempt to decode the message using the DBC file
        decoded_message = DB.decode_message(msg.arbitration_id, msg.data)
        print(f"Decoded: {decoded_message}")
    except KeyError:
        # If the message ID is not in the DBC file, print the raw message
        print(f"Raw: {msg}")


def send_message(msg_name: str, msg_dict: Optional[dict] = None, rtr: bool = False):
    """send message by name. If no msg_dict is provided, use zeros"""
    msg = DB.get_message_by_name(msg_name)
    if rtr:
        # For RTR messages, don't specify the data field
        msg = can.Message(
            arbitration_id=msg.frame_id,
            is_extended_id=False,
            is_remote_frame=True,
        )
    else:
        if msg_dict is None:
            msg_dict = {signal.name: 0 for signal in msg.signals}
        data = msg.encode(msg_dict)
        msg = can.Message(
            arbitration_id=msg.frame_id,
            data=data,
            is_extended_id=False,
        )

    BUS.send(msg)


def send_messages():
    for msg_name in [
        "Axis0_Get_Bus_Voltage_Current",
        "Axis0_Get_Motor_Error",
        "Axis0_Get_Encoder_Error",
        "Axis0_Get_Encoder_Estimates",
        "Axis0_Get_Iq",
        "Axis0_Get_Sensorless_Estimates",
        "Axis0_Clear_Errors",
    ]:
        print(f"Sending {msg_name}")
        send_message(msg_name, rtr=True)
        sleep(0.1)


def main():
    # Start the sending and receiving coroutines

    notifier = can.Notifier(BUS, [print_message])

    # Send some messages
    send_messages()

    print("Cleaning up")
    notifier.stop()  # Stop the notifier when done
    BUS.shutdown()


# Run the main coroutine
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
