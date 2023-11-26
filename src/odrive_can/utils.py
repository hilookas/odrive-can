#!/usr/bin/env python3
"""
 support functions

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from pathlib import Path

import can
import cantools


def get_axis_id(msg: can.Message) -> int:
    """get axis id from message"""
    return msg.arbitration_id >> 5


def extract_ids(can_id: int) -> tuple[int, int]:
    """get axis_id and cmd_id from can_id"""
    cmd_id = can_id & 0x1F  # Extract lower 5 bits for cmd_id
    axis_id = can_id >> 5  # Shift right by 5 bits to get axis_id
    return axis_id, cmd_id


# pylint: disable=import-outside-toplevel
def get_dbc(name: str = "odrive-cansimple-0.5.6"):
    """get the cantools database"""

    # get relative path to db file
    dbc_path = Path(__file__).parent / f"dbc/{name}.dbc"

    return cantools.database.load_file(dbc_path.as_posix())
