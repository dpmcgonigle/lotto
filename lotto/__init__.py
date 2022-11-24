"""
lotto/__init__.py
"""
import os


def loggername() -> str:
    """Get logger name for Lotto"""
    return "LottoLogger"


def basedir() -> str:
    """Return base of lotto repo"""
    return os.path.join(_curdir(), "..")


def _curdir() -> str:
    """Returns current directory"""
    return os.path.dirname(os.path.realpath(__file__))
