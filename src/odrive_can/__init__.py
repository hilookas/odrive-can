__version__ = "0.3.6"

from pathlib import Path

import can
import cantools

LOG_FORMAT = "%(asctime)s [%(name)s] - %(message)s"
TIME_FORMAT = "%H:%M:%S.%f"


# ------support functions


# pylint: disable=import-outside-toplevel
def get_dbc(name: str = "odrive-cansimple-0.5.6"):
    """get the cantools database"""

    # get relative path to db file
    dbc_path = Path(__file__).parent / f"dbc/{name}.dbc"

    return cantools.database.load_file(dbc_path.as_posix())


def get_axis_id(msg: can.Message) -> int:
    """get axis id from message"""
    return msg.arbitration_id >> 5
