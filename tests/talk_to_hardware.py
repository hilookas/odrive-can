#!/usr/bin/env python3

import asyncio
import logging
import argparse
import coloredlogs

from odrive_can import LOG_FORMAT, TIME_FORMAT
from odrive_can.odrive import ODriveCAN
from odrive_can.timer import timeit


def parse_args():
    parser = argparse.ArgumentParser(description="ODrive CAN test script")
    parser.add_argument("--axis-id", type=int, default=1, help="ODrive axis ID")
    parser.add_argument("--interface", type=str, default="slcan0", help="CAN interface")
    return parser.parse_args()


@timeit
async def request(drv: ODriveCAN, method: str):
    """request data from ODrive"""
    log = logging.getLogger()
    log.info(f"Requesting {method}")
    fcn = getattr(drv, method)
    data = await fcn()
    log.info(f"{data=}")


async def main(args):
    log = logging.getLogger()
    coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

    drv = ODriveCAN(axis_id=args.axis_id, interface=args.interface)
    await drv.start()

    try:
        drv.check_alive()
        drv.check_errors()

        for param in [
            "get_bus_voltage_current",
            "get_motor_error",
            "get_encoder_error",
            "get_sensorless_error",
            "get_encoder_estimates",
            "get_encoder_count",
            "get_iq",
            "get_sensorless_estimates",
            "get_adc_voltage",
            "get_controller_error",
        ]:
            await request(drv, param)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e)
    finally:
        drv.stop()
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
