"""
lotto/email/utils.py
"""
import os
from typing import Optional


def verify_credentials() -> bool:
    """Verify email credentials are available in environment
    EMAIL_SEND_ADDRESS and EMAIL_SEND_PASSWORD required

    Returns:
        bool: True if email address and password present
    """
    email_send_address: Optional[str] = os.environ.get("EMAIL_SEND_ADDRESS")
    email_send_password: Optional[str] = os.environ.get("EMAIL_SEND_PASSWORD")
    if email_send_address is None or email_send_password is None:
        return False
    return True
