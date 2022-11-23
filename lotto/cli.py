#! /usr/bin/env python
"""
lotto/cli.py
"""
import logging
from typing import List, Optional

import click

from lotto.notify import verify_credentials

logger = logging.getLogger(__name__)


@click.command()
@click.option("--notify-email", is_flag=True)
@click.option("--notify-email-address", type=str)
@click.option("--notify-email-password", type=str)
def check(
    notify_email: bool,
    notify_email_address: Optional[str],
    notify_email_password: Optional[str],
) -> None:

    logger.info("CHECK START")
    if notify_email and not verify_credentials(
        notify_email_address, notify_email_password
    ):
        raise ValueError("Env missing EMAIL_SEND_ADDRESS and/or EMAIL_SEND_PASSWORD")

    logger.info("CHECK END")


@click.command()
@click.option("s", "--start-date", is_flag=True)
@click.option("e", "--end-date", type=str)
@click.option("-n", "--numbers", type=int, multiple=True)
def add(
    start_date: str,
    end_date: str,
    numbers: List[int],
) -> None:

    logger.info("ADD START")
    logger.debug(f"start_date {start_date}, end_date {end_date}, numbers {numbers}")

    logger.info("ADD END")


@click.command()
def setup() -> None:
    """Create tables in sqlite database"""
    logger.info("SETUP START")

    logger.info("SETUP END")


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
commands.add_command(add)
commands.add_command(setup)

if __name__ == "__main__":
    commands()
