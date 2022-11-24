#! /usr/bin/env python
"""
lotto/cli.py
"""
import logging
import sqlite3
from typing import List, Optional

import arrow
import click

from lotto import loggername
from lotto.db import (
    add_ticket_to_tickets_table,
    check_table_exists,
    create_schedule_table,
    create_tickets_table,
    get_connection,
    query_tickets_table,
)
from lotto.drawings import DrawingLoader
from lotto.notify import verify_credentials
from lotto.tickets import TicketLoader

logger = logging.getLogger(loggername())
TICKET_TABLE_NAME = "TicketTable"
SCHEDULE_TABLE_NAME = "ScheduleTable"


@click.command()
@click.option("-s", "--start-date", type=str)
@click.option("-e", "--end-date", type=str)
@click.option("--notify-email", is_flag=True)
@click.option("--notify-email-address", type=str)
@click.option("--notify-email-password", type=str)
@click.option("--db-path", type=str)
def check(
    start_date: str,
    end_date: str,
    notify_email: bool,
    notify_email_address: Optional[str],
    notify_email_password: Optional[str],
    db_path: Optional[str] = None,
) -> None:

    logger.info("CHECK START")
    if notify_email and not verify_credentials(
        notify_email_address, notify_email_password
    ):
        raise ValueError("Env missing EMAIL_SEND_ADDRESS and/or EMAIL_SEND_PASSWORD")

    conn = get_connection(db_path)
    _validate_tables(conn)

    notification_message = ""

    #   Get Tickets
    tickets = query_tickets_table(
        conn, TICKET_TABLE_NAME, arrow.get(start_date), arrow.get(end_date)
    )

    #   Get Drawings
    for ticket in tickets:
        #   {"2022-11-21": [3, 5, 22, 45, 56, 3]}
        drawing_class = DrawingLoader.load_drawing(
            ticket.lotto_type.value, start_date, end_date
        )
        drawings = drawing_class.get_drawings()
        for drawing_date in drawings.keys():
            notification_message += ticket.check_winnings(
                drawing_date, drawings[drawing_date]
            )

    #   Notify
    logger.info(f"NOTIFICATION: \n{notification_message}")

    logger.info("CHECK END")


@click.command()
@click.option("-l", "--lotto-name", type=str)
@click.option("-s", "--start-date", type=str)
@click.option("-e", "--end-date", type=str)
@click.option("-n", "--numbers", type=int, multiple=True)
@click.option("--db-path", type=str)
def add(
    lotto_name: str,
    start_date: str,
    end_date: str,
    numbers: List[int],
    db_path: Optional[str] = None,
) -> None:
    """Add a lottery ticket to your database
    Example:
    python lotto/cli.py add -l mega_millions -s 20221122 \
        -e 20230127 -n 6 -n 11 -n 13 -n 28 -n 47 -n 25

    Args:
        lotto_name (str): [mega_millions|powerball|etc]
        start_date (str): date that can be interpreted by arrow
        end_date (str): date that can be interpreted by arrow
        numbers (List[int]): your ticket numbers
        db_path (Optional[str], optional): /path/to/file.db (or use default).
    """
    logger.info("ADD START")
    logger.debug(f"start_date {start_date}, end_date {end_date}, numbers {numbers}")

    #   Verify input
    arrow.get(start_date)
    arrow.get(end_date)
    #   Validate info
    ticket = TicketLoader.load_ticket(lotto_name, start_date, end_date, numbers)
    logger.info(f"Validated ticket {ticket}")

    conn = get_connection(db_path)
    add_ticket_to_tickets_table(
        conn, TICKET_TABLE_NAME, lotto_name, start_date, end_date, numbers
    )
    logger.info("ADD END")


@click.command()
@click.option("--db-path", type=str)
def setup(db_path: str) -> None:
    """Create tables in sqlite database"""
    logger.info("SETUP START")
    conn = get_connection(db_path)
    create_tickets_table(conn, TICKET_TABLE_NAME)
    create_schedule_table(conn, SCHEDULE_TABLE_NAME)
    logger.info("SETUP END")


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Print more output.")
def commands(verbose: bool = False) -> None:
    """Base click command group for cli.py

    Args:
        verbose (bool, optional): set logLevel to DEBUG rather than INFO
    """
    # set the logger
    log_level: int = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(log_level)
    logfmt = "[{asctime}][line {lineno}][{funcName}][{levelname}] : {message}"
    datefmt = None
    formatter = logging.Formatter(logfmt, style="{", datefmt=datefmt)

    #   Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


# add all supported CLI commands
commands.add_command(check)
commands.add_command(add)
commands.add_command(setup)


def _validate_tables(conn: sqlite3.Connection) -> None:
    """Raise exception if tables missing"""
    if not check_table_exists(conn, TICKET_TABLE_NAME):
        raise RuntimeError("Ticket Table missing!  Run `lotto setup`")
    if not check_table_exists(conn, SCHEDULE_TABLE_NAME):
        raise RuntimeError("Check Table missing!  Run `lotto setup`")


if __name__ == "__main__":
    commands()
