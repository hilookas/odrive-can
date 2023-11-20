#!/usr/bin/env python3
"""
 simple test of velocity control

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
import time
import odrive  # type: ignore
import odrive.enums as enums  # type: ignore

from odrive_can.tools import UDP_Client


class OdriveError(Exception):
    """custom exception"""


# send data to plotjuggler
udp = UDP_Client()

drv = odrive.find_any()


print(f"Found ODrive {drv.serial_number}")

drv.clear_errors()
drv.axis0.requested_state = enums.AxisState.CLOSED_LOOP_CONTROL
drv.axis0.config.enable_watchdog = False


def check_error(drv):
    """check if there are any errors"""

    names = [
        "error",
        "motor.error",
        "encoder.error",
        "controller.error",
        "sensorless_estimator.error",
    ]

    for name in names:
        var = getattr(drv.axis0, name)
        if var > 0:
            raise OdriveError(f"{name} : {var} ")


# set positiion to zero
drv.axis0.encoder.set_linear_count(0)


setpoints = list(range(0, 50)) + 20 * [50] + list(range(50, 0, -1))


def follow_curve(setpoints, delay=0.1):
    """follow curve consisting of velocity setpoints"""

    # check for errors
    check_error(drv)

    for setpoint in setpoints:
        print(f"{setpoint=}")
        drv.axis0.controller.input_vel = setpoint

        data = {
            "ts": time.time(),
            "sp": setpoint,
            "vel": drv.axis0.encoder.vel_estimate,
            "pos": drv.axis0.encoder.pos_estimate,
        }

        udp.send(data)
        time.sleep(delay)


try:
    while True:
        follow_curve(setpoints)
except KeyboardInterrupt:
    print("interrupted")
