from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

app.conf.beat_schedule = {
    'post_to_leads_every_day': {
        'task': 'email_handler.views.post_to_leads',
        'schedule': crontab(hour=8, minute=3)
    },
    'fetch_unread_emails': {
        'task': 'email_handler.email_fetcher.fetch_unread_emails',
        'schedule': crontab(minute='*/5'),  
    },
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
