from celery import shared_task
from analysis.openrouter_ai import process_email
import logging
from .email_fetcher import fetch_unread_emails

logger = logging.getLogger(__name__)


@shared_task
def analyze_email_response(sender, body, task_type="analyze_response", reference=None):
    category = process_email(task_type, reference, body)
    logger.info(f"Categorized email response from {sender}: {category}")
    return category
