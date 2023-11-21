#!/usr/bin/env python3
"""
 Home odrive

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
ax.requested_state = enums.AxisState.HOMING
sleep(1)
print("Homing...")
while ax.current_state != enums.AxisState.IDLE:
    sleep(1)
    print(".", end="", flush=True)
