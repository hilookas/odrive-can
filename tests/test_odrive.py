from odrive_can.odrive import CommandId


def test_message_ids():
    assert CommandId.ENCODER_ESTIMATE.value == 0x09
