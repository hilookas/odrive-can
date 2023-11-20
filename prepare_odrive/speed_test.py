#!/usr/bin/env python3
"""
 simple test of velocity control

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from time import sleep
import odrive
import odrive.enums as enums

drv = odrive.find_any()

print(f"Found ODrive {drv.serial_number}")

drv.clear_errors()
drv.axis0.requested_state = enums.AxisState.CLOSED_LOOP_CONTROL
drv.axis0.config.enable_watchdog = False


# ramp up
for setpoint in range(0, 50):
    print(f"Setting setpoint to {setpoint}")
    drv.axis0.controller.input_vel = setpoint
    sleep(0.1)

sleep(5)

# ramp down
for setpoint in range(50, 0, -1):
    print(f"Setting setpoint to {setpoint}")
    drv.axis0.controller.input_vel = setpoint
    sleep(0.1)

drv.axis0.requested_state = enums.AxisState.IDLE
