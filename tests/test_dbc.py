from odrive_can import get_dbc


def test_get_db():
    """check database loading"""

    _ = get_dbc()
