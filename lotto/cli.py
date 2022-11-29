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
    add_to_schedule_table,
    check_table_exists,
    create_schedule_table,
    create_tickets_table,
    get_connection,
    query_schedule_table,
    query_tickets_table,
)
from lotto.drawings import DrawingLoader
from lotto.notify import send_notification, verify_credentials
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
@click.option("--destination-email-address", type=str, multiple=True)
@click.option("--db-path", type=str)
@click.option("--show-all-notifications", is_flag=True)
def check(
    start_date: str,
    end_date: str,
    notify_email: bool,
    notify_email_address: Optional[str],
    notify_email_password: Optional[str],
    destination_email_address: Optional[List[str]],
    db_path: Optional[str] = None,
    show_all_notifications: Optional[bool] = None,
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
    logger.debug(f"Checking for tickets between dates {start_date} - {end_date}")
    tickets = query_tickets_table(
        conn, TICKET_TABLE_NAME, arrow.get(start_date), arrow.get(end_date)
    )
    logger.debug(f"Found {len(tickets)} tickets : {tickets}")

    #   Get Drawings
    for ticket in tickets:
        #   {"2022-11-21": [3, 5, 22, 45, 56, 3]}
        assert ticket.ticket_id is not None
        logger.debug(f"Checking ticket {ticket}")
        drawing_class = DrawingLoader.load_drawing(
            ticket.lotto_type.value, start_date, end_date
        )
        drawings = drawing_class.get_drawings()
        for drawing_date in drawings.keys():
            logger.debug(f"Checking drawing_date {drawing_date}")
            ticket_checked = query_schedule_table(
                conn, SCHEDULE_TABLE_NAME, ticket.ticket_id, arrow.get(drawing_date)
            )
            if ticket_checked and not show_all_notifications:
                #   Don't add to message if ticket already checked
                continue
            notification_message += ticket.check_winnings(
                drawing_date, drawings[drawing_date]
            )
            if not ticket_checked:
                add_to_schedule_table(
                    conn, SCHEDULE_TABLE_NAME, ticket.ticket_id, arrow.get(drawing_date)
                )

    #   Notify
    logger.info(f"NOTIFICATION: \n{notification_message}")

    if notify_email and len(notification_message) > 0:
        assert destination_email_address is not None
        assert notify_email_address is not None
        assert notify_email_password is not None
        for destination_email in destination_email_address:
            send_notification(
                notify_email_address,
                notify_email_password,
                f"New lottery drawings {start_date} - {end_date}",
                notification_message,
                destination_email,
            )

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
