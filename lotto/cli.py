#! /usr/bin/env python
"""
lotto/cli.py
"""
import logging

import click

from lotto.email.utils import verify_credentials

logger = logging.getLogger(__name__)


@click.command()
@click.option("--notify-email", is_flag=True)
def check(notify_email: bool) -> None:

    logger.info("CHECK START")
    if notify_email and not verify_credentials():
        raise ValueError("Env missing EMAIL_SEND_ADDRESS and/or EMAIL_SEND_PASSWORD")
    logger.info("CHECK END")


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Print more output.")
def commands(verbose: bool = False) -> None:
    """Base click command group for cli.py

    Args:
        verbose (bool, optional): set logLevel to DEBUG rather than INFO
    """
    # set the logger
    #   log_file = f"{os.path.splitext(__file__)[0]}.log"
    log_level: int = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(log_level)


# add all supported CLI commands
commands.add_command(check)

if __name__ == "__main__":
    commands()
