import logging

import aiosmtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("bidpilot.email")


def dev_mode_no_smtp() -> bool:
    """True when there's no real SMTP configured and we're not in production — the caller
    should surface a debug_link in the API response instead of relying on a real inbox."""
    return not settings.smtp_host and settings.environment == "development"


async def send_email(to: str, subject: str, body: str) -> None:
    if not settings.smtp_host:
        if settings.environment != "development":
            raise RuntimeError("SMTP_HOST is not configured and ENVIRONMENT is not 'development'")
        logger.info("DEV EMAIL to=%s subject=%s\n%s", to, subject, body)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=settings.smtp_use_tls,
    )
