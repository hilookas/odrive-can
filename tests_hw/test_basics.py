import logging
from time import sleep
import time

import pytest

from odrive_can.odrive import CommandId, ODriveCAN

# pylint: disable=protected-access

INTERFACE = "slcan0"
drv = ODriveCAN(axis_id=1, channel=INTERFACE)


def test_heartbeat():
    sleep(0.5)
    drv.check_alive()
    drv.check_errors()


def test_ignore():
    # ignore encoder estimate
    logging.info("Ignoring encoder estimate")
    drv.ignore_message(CommandId.ENCODER_ESTIMATE)
    assert 0x09 in drv._ignored_messages
    sleep(0.5)
    logging.info("Allowing encoder estimate")
    drv.allow_message(CommandId.ENCODER_ESTIMATE)
    assert 0x09 not in drv._ignored_messages
    sleep(0.5)

    drv.check_alive()
    drv.check_errors()


def test_request_raw():
    # bus voltage and current
    drv._send_message("Get_Bus_Voltage_Current", rtr=True)
    sleep(0.1)
    drv._clear_request()
    drv.check_alive()
    drv.check_errors()


@pytest.mark.asyncio
async def test_request():
    # bus voltage and current
    logging.info("Requesting bus voltage and current")
    drv.ignore_message(CommandId.ENCODER_ESTIMATE)

    for _ in range(4):
        t_start = time.perf_counter()
        data = await drv.request("Get_Bus_Voltage_Current")
        t_end = time.perf_counter()
        logging.info(f"Request took {t_end-t_start:.3f} s")
    assert "Bus_Voltage" in data
    assert "Bus_Current" in data
    sleep(0.1)

    drv.check_alive()
    drv.check_errors()
