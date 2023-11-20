#!/usr/bin/env python3
"""
 simple test of velocity control

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from time import sleep
import odrive  # type: ignore
import odrive.enums as enums  # type: ignore

drv = odrive.find_any()

print(f"Found ODrive {drv.serial_number}")

drv.clear_errors()
drv.axis0.requested_state = enums.AxisState.CLOSED_LOOP_CONTROL
drv.axis0.config.enable_watchdog = False


def is_error(drv):
    """check if there are any errors"""
    ax = drv.axis0

    for var in [
        ax.error,
        ax.motor.error,
        ax.encoder.error,
        ax.controller.error,
        ax.sensorless_estimator.error,
    ]:
        if var > 0:
            return True

    return False


# check for errors
if is_error(drv):
    print("ERROR found, exiting")
    exit(1)

# set positiion to zero
drv.axis0.encoder.set_linear_count(0)


setpoints = list(range(0, 50)) + 20 * [50] + list(range(50, 0, -1))


def follow_curve(setpoints, delay=0.1):
    """follow curve consisting of velocity setpoints"""

    for setpoint in setpoints:
        print(f"Setting setpoint to {setpoint}")
        drv.axis0.controller.input_vel = setpoint
        sleep(delay)
        # print current velocity
        print(f"Current velocity: {drv.axis0.encoder.vel_estimate}")
        # print current position
        print(f"Current position: {drv.axis0.encoder.pos_estimate}")


follow_curve(setpoints)
