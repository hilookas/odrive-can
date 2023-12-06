#!/usr/bin/env python3
"""
 Demonstration of velocity control using CAN interface

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging

from odrive_can.odrive import ODriveCAN
from odrive_can.setpoints import sawtooth_generator
from odrive_can.tools import UDP_Client

from .position_control import feedback_callback

SETPOINT_DELAY = 0.1


log = logging.getLogger("pos_ctl")
udp = UDP_Client()


async def configure_controller(drv: ODriveCAN):
    """setup control parameters"""

    # reset encoder
    drv.set_linear_count(0)

    drv.set_controller_mode("VELOCITY_CONTROL", "VEL_RAMP")

    # set position control mode
    await drv.set_axis_state("CLOSED_LOOP_CONTROL")
    drv.check_errors()


async def main_loop(drv: ODriveCAN, amplitude: float = 40.0):
    """velocity control demo"""

    log.info("-----------Running velocity control-----------------")

    drv.feedback_callback = feedback_callback
    await drv.start()

    await asyncio.sleep(0.5)
    drv.check_alive()
    drv.clear_errors()
    drv.check_errors()

    await configure_controller(drv)

    # make setpoint generator
    setpoint_gen = sawtooth_generator(roc=10.0, max_val=40.0)

    drv.set_input_pos(amplitude)

    await asyncio.sleep(2)

    try:
        while True:
            drv.check_errors()
            setpoint = next(setpoint_gen)

            drv.set_input_vel(setpoint)
            await asyncio.sleep(SETPOINT_DELAY)

    except KeyboardInterrupt:
        log.info("Stopping")
    finally:
        drv.stop()
        await asyncio.sleep(0.5)


def main(axis_id: int, interface: str, amplitude: float = 40.0):
    print("Starting velocity control demo, press CTRL+C to exit")
    drv = ODriveCAN(axis_id, interface)

    try:
        asyncio.run(main_loop(drv, amplitude))
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt")


if __name__ == "__main__":
    import coloredlogs  # type: ignore

    from odrive_can import LOG_FORMAT, TIME_FORMAT  # pylint: disable=ungrouped-imports

    coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

    main(1, "slcan0")
