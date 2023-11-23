#!/usr/bin/env python3
"""
 demonstrate usage of OdriveCAN class

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging

import coloredlogs  # type: ignore

from odrive_can import LOG_FORMAT, TIME_FORMAT
from odrive_can.odrive import CommandId, ODriveCAN
from odrive_can.timer import timeit

log = logging.getLogger()
coloredlogs.install(level="DEBUG", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)


AXIS_ID = 1
INTERFACE = "slcan0"


def position_callback(data):
    log.info(f"Position: {data}")


async def get_bus_voltage_current(drv: ODriveCAN):
    """request bus voltage and current"""

    @timeit
    async def request(drv: ODriveCAN):
        data = await drv.get_bus_voltage_current()
        log.info(f"{data=}")

    log.info("Requesting bus voltage and current")
    # request bus voltage and current
    for _ in range(4):
        log.info("------------------------------")
        try:
            await request(drv)

        except Exception as e:  # pylint: disable=broad-except
            log.warning(e)
        await asyncio.sleep(0.1)


async def change_axis_state(drv: ODriveCAN):
    """change axis state to closed loop control"""
    # get curent axis state
    log.info(f"Axis state: {drv.axis_state}")
    drv.set_axis_state("CLOSED_LOOP_CONTROL")
    await asyncio.sleep(0.5)  #  wait for heartbeat update
    log.info(f"Axis state: {drv.axis_state}")


async def main():
    drv = ODriveCAN(axis_id=AXIS_ID, channel=INTERFACE)
    drv.position_callback = position_callback
    await drv.start()

    # log some messages
    await asyncio.sleep(1.0)

    await change_axis_state(drv)

    # set log level to INFO
    coloredlogs.set_level(logging.INFO)

    # ignore encoder estimate messages
    drv.ignore_message(CommandId.ENCODER_ESTIMATE)

    # request bus voltage and current
    await get_bus_voltage_current(drv)

    # enable encoder feedback
    drv.allow_message(CommandId.ENCODER_ESTIMATE)

    # reset encoder
    drv.reset_linear_count()
    await asyncio.sleep(1.0)

    # shutdown
    drv.stop()
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
