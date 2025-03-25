from celery import shared_task
from analysis.openrouter_ai import analyze_response
import logging

logger = logging.getLogger(__name__)

@shared_task
def analyze_email_response(sender, body):
    category = analyze_response(body)
    logger.info(f"Categorized email response from {sender}: {category}")
    return category
