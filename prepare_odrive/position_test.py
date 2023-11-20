#!/usr/bin/env python3
"""
 simple acceleration test

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
import time
import asyncio
import odrive  # type: ignore
import odrive.enums as enums  # type: ignore
from utils import check_error

from odrive_can.tools import UDP_Client

DURATION = 5
SETPOINT = 20

drv = odrive.find_any()
ax = drv.axis0

print(f"Found ODrive {drv.serial_number}")

drv.clear_errors()
ax.requested_state = enums.AxisState.CLOSED_LOOP_CONTROL

check_error(drv)

ax.controller.config.control_mode = enums.ControlMode.POSITION_CONTROL
ax.controller.config.vel_ramp_rate = 1  # this does not do anything
ax.motor.config.current_lim = 1.5

# position control
ax.controller.config.pos_gain = 3.0


async def feedback_loop():
    udp = UDP_Client()

    while True:
        check_error(drv)

        data = {
            "ts": time.time(),
            "sp": ax.controller.input_pos,
            "vel": ax.encoder.vel_estimate,
            "pos": ax.encoder.pos_estimate,
        }

        udp.send(data)
        await asyncio.sleep(0.05)


async def setpoint_loop():
    while True:
        ax.controller.input_pos = SETPOINT
        await asyncio.sleep(DURATION)
        ax.controller.input_pos = -SETPOINT
        await asyncio.sleep(DURATION)


async def main():
    await asyncio.gather(feedback_loop(), setpoint_loop())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    ax.controller.input_vel = 0
    ax.requested_state = enums.AxisState.IDLE
