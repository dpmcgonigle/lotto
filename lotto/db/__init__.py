"""
lotto/db/__init__.py
"""
import os

from lotto import basedir


def _get_db_path() -> str:
    """Get JSON config"""
    return os.path.join(basedir(), "data", "db", "database.db")
