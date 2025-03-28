from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

app.conf.beat_schedule = {

    'fetch_pending_campaign': {
        'task': 'campaign.tasks.fetch_pending_campaigns',
        'schedule': crontab(minute='*/1'),
        'options': {'expires': 50},
    },

    'fetch_unread_emails': {
        'task': 'email_handler.email_fetcher.fetch_unread_emails',
        'schedule': crontab(minute='*/1'),
    },

}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
