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
    """Best-effort — a notification email failing (misconfigured SMTP, provider outage, etc.)
    must never fail the operation that triggered it (signup, invite, password reset). Errors
    are logged, not raised; callers that need to know delivery actually happened should check
    for that explicitly rather than relying on this not raising."""
    if not settings.smtp_host:
        if settings.environment != "development":
            logger.error("SMTP_HOST is not configured and ENVIRONMENT is not 'development' — email not sent")
            return
        logger.info("DEV EMAIL to=%s subject=%s\n%s", to, subject, body)
        return

    if not settings.smtp_from_email:
        logger.error("SMTP_HOST is configured but SMTP_FROM_EMAIL is not set — email not sent")
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            start_tls=settings.smtp_use_tls,
        )
    except Exception:
        logger.exception("Failed to send email to=%s subject=%s", to, subject)
