import os

from celery import Celery
from celery.schedules import crontab

from eticketing_api import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eticketing_api.settings")

celery = Celery("eticketing_api")

celery.config_from_object("django.conf:settings", namespace="CELERY")

celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

celery.conf.beat_schedule = {
    "reminders": {"task": "send_out_reminders", "schedule": crontab(minute=0, hour=12)},
    "promos": {"task": "send_out_promos", "schedule": crontab(hour=8)},
    "cleanup_notifications": {
        "task": "cleanup_notifications",
        "schedule": crontab(day_of_week="sun"),
    },
    "reconcile_payments": {
        "task": "reconcile_payments",
        "schedule": crontab(day_of_week="sun", hour=5),
    },
}
