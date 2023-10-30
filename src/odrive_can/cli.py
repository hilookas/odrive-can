#!/usr/bin/env python3
"""
odrive_can CLI
"""

import functools
import logging

import click
import coloredlogs  # type: ignore

from odrive_can import LOG_FORMAT, TIME_FORMAT

log = logging.getLogger()
coloredlogs.install(level="INFO", fmt=LOG_FORMAT, datefmt=TIME_FORMAT)

# pylint: disable=import-outside-toplevel, unused-argument

# ------------------ helpers


def common_cli(func):
    """common CLI options"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # turn on debugging
        debug = kwargs.get("debug", False)
        if debug:
            coloredlogs.set_level("DEBUG")

        return func(*args, **kwargs)

    return wrapper


@click.group()
def cli():
    pass  # pragma: no cover


@cli.command()
def info():
    """Print package info"""
    from .version import get_version

    print(get_version())


@cli.command()
@click.option("--axis-id", default=0, help="ODrive axis ID")
@click.option("--channel", default="vcan0", help="CAN channel")
@click.option("--debug", is_flag=True, help="Turn on debugging")
@common_cli
def mock(axis_id, channel, debug):
    """Mock ODrive CAN interface"""
    from .mock import main

    main(axis_id=axis_id, channel=channel)


@cli.command()
@click.option("--channel", default="vcan0", help="CAN channel")
@click.option("--debug", is_flag=True, help="Turn on debugging")
@common_cli
def inspect(channel, debug):
    """Inspect and decode ODrive CAN messages"""
    from .inspector import main

    main(channel=channel)


if __name__ == "__main__":
    cli()  # pragma: no cover
