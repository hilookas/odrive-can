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


@timeit
async def get_bus_voltage_current(drv: ODriveCAN):
    data = await drv.request("Get_Bus_Voltage_Current")
    log.info(f"Bus voltage: {data['Bus_Voltage']:.2f} V")


async def main():
    drv = ODriveCAN(axis_id=1, channel=INTERFACE)

    # ignore encoder estimate messages
    drv.ignore_message(CommandId.ENCODER_ESTIMATE)

    # request bus voltage and current
    for idx in range(4):
        await get_bus_voltage_current(drv)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
