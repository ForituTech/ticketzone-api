from datetime import date, timedelta

from celery import shared_task
from django.db.models.query import QuerySet

from notifications.models import Notification


@shared_task(name="cleanup_notifications")
def cleanup_notifications() -> None:
    last_week = date.today() - timedelta(weeks=1)
    notifications: QuerySet[Notification] = Notification.objects.filter(
        created_at__lte=last_week
    )
    for notification in notifications:
        notification.delete()
