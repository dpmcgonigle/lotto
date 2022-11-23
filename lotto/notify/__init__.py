"""
lotto/email/__init__.py
"""
import os
import re
import smtplib
from email.message import EmailMessage
from typing import Optional


def verify_credentials(
    notify_email_address: Optional[str] = None,
    notify_email_password: Optional[str] = None,
) -> bool:
    """Verify email credentials exist and are valid
    First check arguments, then environment
    Environment vars : EMAIL_SEND_ADDRESS and EMAIL_SEND_PASSWORD

    Args:
        notify_email_address (str, optional): email address
        notify_email_password (str, optional): email password

    Returns:
        bool: True if email address and password present
    """
    #   Get email
    if notify_email_address is not None:
        email_send_address: Optional[str] = notify_email_address
    else:
        email_send_address = os.environ.get("EMAIL_SEND_ADDRESS")

    #   Get password
    if notify_email_password is not None:
        email_send_password: Optional[str] = notify_email_password
    else:
        email_send_password = os.environ.get("EMAIL_SEND_PASSWORD")

    #   Validate
    if email_send_address is None or email_send_password is None:
        return False
    if not _validate_email_address(email_send_address):
        return False

    return True


def send_notification(
    notify_email_address: str,
    notify_email_password: str,
    notification_subject: str,
    notification_body: str,
    destination_email_address: str,
):
    """Send an email to notify

    Args:
        notify_email_address (str): Sender email (must be gmail)
        notify_email_password (str): Sender pw
        notification_subject (str): Message subject
        notification_body (str): Message body
        destination_email_address (str): Receiver email
    """
    if not notify_email_address.lower().endswith("gmail.com"):
        raise ValueError(
            f"notify_email_address must be gmail, got {notify_email_address}"
        )

    #   Connection
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(notify_email_address, notify_email_password)

    #   Message
    msg = EmailMessage()
    msg["From"] = notify_email_address
    msg["To"] = destination_email_address
    msg["Subject"] = f"[lotto.py] : {notification_subject}"
    msg.set_content(notification_body)

    #   Send away!
    server.sendmail(destination_email_address, notify_email_address, msg.as_string())
    server.quit()


def _validate_email_address(email_address: str) -> bool:
    """Determine if email address is valid"""
    regex = re.compile(
        r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    )
    return re.fullmatch(regex, email_address) is not None
