from django.core.management.base import BaseCommand
import logging
from email_handler.email_fetcher import fetch_unread_emails

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch unread emails and send for sentiment analysis'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'Starting to fetch unread emails...'))

        try:
            # Run the fetch_unread_emails task synchronously for testing
            result = fetch_unread_emails()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully fetched and processed emails: {result}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error fetching emails: {str(e)}'))
            logger.error(f'Error in fetch_emails command: {str(e)}')
