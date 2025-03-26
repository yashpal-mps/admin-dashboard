import requests
from .apps import Communication
from django.conf import settings

MAILGUN_API_KEY = settings.MAILGUN_API_KEY
MAILGUN_DOMAIN = settings.MAILGUN_DOMAIN

class EmailService(Communication):
    """Handles sending emails using Mailgun."""

    def __init__(self, recipient, message):
        super().__init__(recipient, message)


    def send_message(self):
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Your App <noreply@{MAILGUN_DOMAIN}>",
                "to": self.recipient,
                "subject": "Automated Email",
                "text": self.message,
            },
        )
        return response.json()
