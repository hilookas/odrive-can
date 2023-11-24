#!/usr/bin/env python3
"""
 Demonstration of position control using CAN interface

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging
from odrive_can.odrive import ODriveCAN
from odrive_can.tools import UDP_Client

SETTLE_TIME = 5.0  # settle time in [s]


log = logging.getLogger("pos_ctl")
udp = UDP_Client()

setpoint: float = 40.0


def position_callback(data):
    """position callback, send data to UDP client"""
    data["setpoint"] = setpoint
    udp.send(data)


async def configure_controller(drv: ODriveCAN, input_mode: str = "POS_FILTER"):
    """setup control parameters"""

    # set parameters
    drv.set_pos_gain(5.0)

    drv.set_traj_vel_limit(40.0)
    drv.set_traj_accel_limits(40.0, 40.0)

    # reset encoder
    drv.set_linear_count(0)

    drv.set_controller_mode("POSITION_CONTROL", input_mode)

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

    await configure_controller(drv, input_mode)

    # start running

    drv.set_input_pos(setpoint)
    await asyncio.sleep(2)

    idx = 0
    try:
        while True:
            drv.check_errors()

            drv.set_input_pos(setpoint)
            idx += 1
            await asyncio.sleep(SETTLE_TIME)
            setpoint = -setpoint

    except KeyboardInterrupt:
        log.info("Stopping")
    finally:
        drv.stop()
        await asyncio.sleep(0.5)


def main(axis_id: int, interface: str, input_mode: str = "POS_FILTER"):
    print("Starting position control demo, press CTRL+C to exit")
    drv = ODriveCAN(axis_id, interface)

    try:
        asyncio.run(main_loop(drv, input_mode))
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt")


if __name__ == "__main__":
    import coloredlogs  # type: ignore
    from odrive_can import LOG_FORMAT, TIME_FORMAT  # pylint: disable=ungrouped-imports

    coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

    main(1, "slcan0")
