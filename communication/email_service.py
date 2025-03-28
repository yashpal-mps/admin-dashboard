import requests
from .apps import Communication
from django.conf import settings
import logging
from django.core.mail import send_mail

# MAILGUN_API_KEY = settings.MAILGUN_API_KEY
# MAILGUN_DOMAIN = settings.MAILGUN_DOMAIN
logger = logging.getLogger(__name__)


class EmailService(Communication):
    """Handles sending emails using Mailgun."""

    def __init__(self, recipient, message):
        super().__init__(recipient, message)

    def send_message(self, lead):
        send_mail(
            subject=lead.reference,
            message=self.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.recipient],
            fail_silently=False,
        )
