__version__ = "0.0.1"


LOG_FORMAT = "%(asctime)s [%(name)s] - %(message)s"
TIME_FORMAT = "%H:%M:%S.%f"


# pylint: disable=import-outside-toplevel
def get_dbc(name: str = "odrive-cansimple-0.5.6"):
    """get the cantools database"""

    from pathlib import Path
    import cantools

    # get relative path to db file
    dbc_path = Path(__file__).parent / f"dbc/{name}.dbc"

    return cantools.database.load_file(dbc_path.as_posix())
