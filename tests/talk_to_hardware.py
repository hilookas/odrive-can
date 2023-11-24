# Not a pytest. Just a script to test the hardware.

import asyncio
import logging

import coloredlogs  # type: ignore

from odrive_can import LOG_FORMAT, TIME_FORMAT
from odrive_can.odrive import CommandId, ODriveCAN
from odrive_can.timer import timeit

log = logging.getLogger()
coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)


AXIS_ID = 1
INTERFACE = "slcan0"


@timeit
async def request(drv: ODriveCAN, method: str):
    """request data from ODrive"""
    log.info(f"Requesting {method}")
    fcn = getattr(drv, method)
    data = await fcn()
    log.info(f"{data=}")


async def main():
    drv = ODriveCAN(axis_id=AXIS_ID, interface=INTERFACE)
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
    asyncio.run(main())
