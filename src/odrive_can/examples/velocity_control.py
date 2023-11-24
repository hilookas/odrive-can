#!/usr/bin/env python3
"""
 Demonstration of velocity control using CAN interface

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging
from odrive_can.odrive import ODriveCAN
from odrive_can.tools import UDP_Client
from odrive_can.setpoints import sawtooth_generator

SETPOINT_DELAY = 0.1


log = logging.getLogger("pos_ctl")
udp = UDP_Client()

setpoint: float = 40.0  # velocity setpoint in [rev/s]


def position_callback(data):
    """position callback, send data to UDP client"""
    data["setpoint"] = setpoint
    udp.send(data)


async def configure_controller(drv: ODriveCAN):
    """setup control parameters"""

    # reset encoder
    drv.set_linear_count(0)

    drv.set_controller_mode("VELOCITY_CONTROL", "VEL_RAMP")

    # set position control mode
    drv.set_axis_state("CLOSED_LOOP_CONTROL")
    await asyncio.sleep(0.5)  #  wait for heartbeat update
    drv.check_errors()


async def main_loop(drv: ODriveCAN, input_mode: str = "POS_FILTER"):
    """position demo"""

    global setpoint  # pylint: disable=global-statement

    log.info("-----------Running position control-----------------")

    drv.position_callback = position_callback
    await drv.start()

    await asyncio.sleep(0.5)
    drv.check_alive()
    drv.clear_errors()
    drv.check_errors()

    await configure_controller(drv)

    # make setpoint generator
    setpoint_gen = sawtooth_generator(roc=10.0, max_val=40.0)

    drv.set_input_pos(setpoint)
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


def main(axis_id: int, interface: str):
    print("Starting velocity control demo, press CTRL+C to exit")
    drv = ODriveCAN(axis_id, interface)

    try:
        asyncio.run(main_loop(drv))
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt")


if __name__ == "__main__":
    import coloredlogs  # type: ignore
    from odrive_can import LOG_FORMAT, TIME_FORMAT  # pylint: disable=ungrouped-imports

    coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

    main(1, "slcan0")
