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


INTERFACE = "slcan0"


async def get_bus_voltage_current(drv: ODriveCAN):
    """request bus voltage and current"""

    @timeit
    async def request(drv: ODriveCAN):
        data = await drv.request("Get_Bus_Voltage_Current")
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


async def main():
    drv = ODriveCAN(axis_id=1, channel=INTERFACE)
    await drv.start()

    # log some messages
    await asyncio.sleep(1.0)

    coloredlogs.set_level(logging.INFO)

    # ignore encoder estimate messages
    drv.ignore_message(CommandId.ENCODER_ESTIMATE)

    # request bus voltage and current
    await get_bus_voltage_current(drv)

    drv.stop()
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
