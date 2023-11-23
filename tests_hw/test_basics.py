import logging
from time import sleep
from odrive_can.odrive import ODriveCAN, CommandId

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


def test_request():
    # bus voltage and current
    drv._send_message("Get_Bus_Voltage_Current", rtr=True)
    sleep(0.1)
