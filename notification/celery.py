import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification.settings')

app = Celery('notification')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Каждое утро в 5:30 будет отправлятся статистика на email
app.conf.beat_schedule = {
    'send_mailing_stats_every_day': {
        'task': 'mailing.tasks.send_daily_stats_email',
        'schedule': crontab(hour='05', minute='30')
    }
}

app.autodiscover_tasks()
