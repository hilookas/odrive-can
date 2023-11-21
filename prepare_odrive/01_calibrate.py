#!/usr/bin/env python3
"""
 Set odrive can parameters

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from time import sleep

import odrive  # type: ignore
import odrive.enums as enums  # type: ignore

from utils import check_error


drv = odrive.find_any()
print(f"Found ODrive {drv.serial_number}")

drv.clear_errors()
check_error(drv)

ax = drv.axis0
ax.requested_state = enums.AxisState.FULL_CALIBRATION_SEQUENCE
sleep(1)
print("Calibrating...")
while ax.current_state != enums.AxisState.IDLE:
    sleep(1)
    print(".", end="", flush=True)

ax.motor.config.pre_calibrated = True
ax.encoder.config.pre_calibrated = True

drv.save_configuration()

print("Done")

drv.reboot()
