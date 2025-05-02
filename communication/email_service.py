import requests
from .apps import Communication
from django.conf import settings
import logging
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


class EmailService(Communication):

    def __init__(self, recipient,subject , message):
        self.subject = subject
        super().__init__(recipient, message)

    def send_message(self):
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.recipient],
            fail_silently=False,
        )
