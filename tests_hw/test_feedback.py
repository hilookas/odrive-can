from time import sleep
import netifaces
from odrive_can.odrive import ODriveCAN

INTERFACE = "slcan0"


def test_interface_present():
    """check that can BUS device is present"""
    assert INTERFACE in netifaces.interfaces()  # pylint: disable=c-extension-no-member


def test_heartbeat():
    drv = ODriveCAN(axis_id=1, channel=INTERFACE)
    sleep(1.5)
    assert drv.is_alive()
