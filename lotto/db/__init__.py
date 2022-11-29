"""
lotto/db/__init__.py
"""
import logging
import os
import sqlite3
from typing import List, Optional

import arrow

from lotto import basedir, loggername
from lotto.tickets import LotteryTicket, TicketLoader

logger = logging.getLogger(loggername())


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get sqlite3 connection

    Args:
        db_path (Optional[str], optional): path to file.db; default if None

    Returns:
        sqlite3.Connection: sqlite3 connection to a database file
    """
    if db_path is None:
        db_path = _get_db_path()
    return sqlite3.connect(db_path)


def create_tickets_table(conn: sqlite3.Connection, ticket_table_name: str) -> None:
    sql = f"""
        CREATE TABLE IF NOT EXISTS {ticket_table_name} (
            TicketKey INTEGER PRIMARY KEY AUTOINCREMENT,
            LottoName varchar(255),
            StartDate varchar(255),
            EndDate varchar(255),
            Numbers varchar(255)
        );
    """
    conn.execute(sql)


def add_ticket_to_tickets_table(
    conn: sqlite3.Connection,
    ticket_table_name: str,
    lotto_name: str,
    start_date: str,
    end_date: str,
    numbers: List[int],
) -> None:

    numbers_str = " ".join([str(x) for x in numbers])
    logger.info(f"numbers_str {numbers_str}")
    sql = f"""
        INSERT INTO {ticket_table_name} (LottoName, StartDate, EndDate, Numbers)
        VALUES ('{lotto_name}', '{start_date}', '{end_date}', '{numbers_str}');
    """
    conn.execute(sql)
    conn.commit()


def query_tickets_table(
    conn: sqlite3.Connection,
    ticket_table: str,
    start_date: arrow.Arrow,
    end_date: arrow.Arrow,
) -> List[LotteryTicket]:
    """Get Lottery Tickets in date range

    Args:
        conn (sqlite3.Connection): sqlite connection
        start_date (arrow.Arrow): ticket query start date
        end_date (arrow.Arrow): ticket query start date

    Returns:
        LotteryTicket: [PowerballTicket|MegaMillionsTicket|etc]
    """
    sql = f"""SELECT * from {ticket_table}"""
    #   Results like:
    #   [(1, 'powerball', '20221122', '20230127', '6 11 13 28 47 25'),
    cursor = conn.execute(sql)
    results = cursor.fetchall()
    all_tickets: List[LotteryTicket] = []
    logger.debug(f"query_tickets_table results {results}")
    for result in results:
        ticket = TicketLoader.load_ticket(
            lotto_name=result[1],
            start_date=result[2],
            end_date=result[3],
            numbers=[int(x) for x in result[4].split(" ")],
            ticket_id=result[0],
        )
        #   Check for overlap
        if (
            start_date <= ticket.start_date <= end_date
            or start_date <= ticket.end_date <= end_date
            or (ticket.start_date <= start_date and ticket.end_date >= end_date)
        ):
            all_tickets.append(ticket)
    return all_tickets


def query_schedule_table(
    conn: sqlite3.Connection,
    schedule_table: str,
    ticket_id: int,
    check_date: arrow.Arrow,
) -> bool:
    """Check to see if a ticket is already in the schedule table"""
    schedule_date = check_date.strftime("%Y%m%d")
    sql = f"""SELECT * from {schedule_table} where TicketKey={ticket_id} \
        and ScheduleDate='{schedule_date}'"""
    cursor = conn.execute(sql)
    results = cursor.fetchall()
    return len(results) > 0


def add_to_schedule_table(
    conn: sqlite3.Connection,
    schedule_table: str,
    ticket_id: int,
    check_date: arrow.Arrow,
) -> None:
    """Check to see if a ticket is already in the schedule table"""
    schedule_date = check_date.strftime("%Y%m%d")
    sql = f"""INSERT INTO {schedule_table} (ScheduleDate, TicketKey)
        VALUES ('{schedule_date}', {ticket_id})"""
    conn.execute(sql)
    conn.commit()


def create_schedule_table(conn: sqlite3.Connection, schedule_table_name: str) -> None:
    sql = f"""
        CREATE TABLE IF NOT EXISTS {schedule_table_name} (
            ScheduleDate varchar(255),
            TicketKey varchar(255)
        );
    """
    conn.execute(sql)


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check to see if sqlite table exists"""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] == table_name:
            return True
    return False


def _get_db_path() -> str:
    """Get JSON config"""
    return os.path.join(basedir(), "data", "db", "database.db")
