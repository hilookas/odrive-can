import pytest
import netifaces

INTERFACE = "slcan0"


def test_interface_present():
    """check that can BUS device is present"""
    assert INTERFACE in netifaces.interfaces()  # pylint: disable=c-extension-no-member
