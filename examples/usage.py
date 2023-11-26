import asyncio
from odrive_can import ODriveCAN

AXIS_ID = 1
INTERFACE = "slcan0"
SETPOINT = 50


def position_callback(data: dict):
    """called on position estimate"""
    print(data)


async def main():
    """connect to odrive"""
    drv = ODriveCAN(axis_id=AXIS_ID, interface=INTERFACE)

    # set up callback (optional)
    drv.position_callback = position_callback

    # start
    await drv.start()

    # check errors (raises exception if any)
    drv.check_errors()

    # set controller mode
    drv.set_controller_mode("POSITION_CONTROL", "POS_FILTER")

    # set axis state
    await drv.set_axis_state("CLOSED_LOOP_CONTROL")

    # set position gain
    drv.set_pos_gain(3.0)

    # reset encoder
    drv.set_linear_count(0)

    for _ in range(4):
        # setpoint
        drv.set_input_pos(SETPOINT)
        await asyncio.sleep(5.0)
        drv.set_input_pos(-SETPOINT)
        await asyncio.sleep(5.0)


asyncio.run(main())
