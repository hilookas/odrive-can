#!/usr/bin/env python3
"""
odrive_can CLI
"""

import click
from .version import get_version


@click.group()
def cli():
    pass  # pragma: no cover


@cli.command()
def info():
    """ Print package info """
    print(get_version())


cli.add_command(info)

if __name__ == "__main__":
    cli()  # pragma: no cover
