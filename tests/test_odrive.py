from odrive_can.odrive import CommandId, ODriveCAN


def test_message_ids():
    assert CommandId.ENCODER_ESTIMATE.value == 0x09
