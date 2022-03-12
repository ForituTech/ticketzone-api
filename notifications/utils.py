from typing import Any, Dict, List, Optional, Sequence

from django.contrib import admin, messages
from django.core.mail import EmailMessage
from django.db.models.query import QuerySet
from django.http import HttpRequest

from notifications.constants import NotificationsChannels
from notifications.models import Notification
from notifications.pusher import pusher_client
from notifications.sms import sms_client
from partner.models import Person

retries = 0


def send_email(
    person: Person,
    header: str,
    body: str,
    attachments: Sequence[Any] = [],
    html: bool = False,
    retry: int = 0,
) -> bool:
    if retries == 5:
        return False
    email = EmailMessage(
        subject=header,
        body=body,
        to=[person.email],
    )
    email.attach()
    failed = email.send(fail_silently=True)
    if failed:
        send_email(person, header, body, attachments, html, retry=retry + 1)
    Notification.objects.create(
        person=person,
        channel=NotificationsChannels.EMAIL.value,
        has_data=True if len(attachments) else False,
    )
    return True


def send_multi_email(
    persons: List[Person],
    header: str,
    body: str,
    attachments: Sequence[Any] = [],
    html: bool = False,
    retry: int = 0,
) -> bool:
    if retries == 5:
        return False
    email = EmailMessage(
        subject=header,
        body=body,
        to=[person.email for person in persons],
    )
    email.attach()
    failed = email.send(fail_silently=True)
    if failed:
        send_multi_email(persons, header, body, attachments, html, retry=retry + 1)
    for person in persons:
        Notification.objects.create(
            person=person,
            channel=NotificationsChannels.EMAIL.value,
            has_data=True if len(attachments) else False,
        )
    return True


def send_push_notification(
    person: Person, body: str, data: Optional[Dict[str, Any]] = dict()
) -> Optional[Dict[str, str]]:
    notification: Notification = Notification.objects.create(
        person_id=person.id,
        message=body,
        channel=NotificationsChannels.PUSHER.value,
        has_data=data is None,
    )
    pusher_notification = pusher_client.push_web_notification(
        user_ids=[str(person.id)], body=body, data=data
    )
    notification.sent = pusher_notification is None
    notification.save() if pusher_notification else None
    return pusher_notification


def send_sms(person: Person, message: str) -> None:
    notification: Notification = Notification.objects.create(
        person=person,
        message=message,
        channel=NotificationsChannels.SMS.value,
        has_data=False,
    )
    sms_client.send(message, [person.phone_number])
    notification.sent = True
    notification.save()


@admin.action(description="Resend Notification")
def resend_notification(
    modeladmin: Any, request: HttpRequest, queryset: QuerySet[Notification]
) -> None:
    for notification in queryset:
        if notification.channel != NotificationsChannels.SMS.value:
            messages.error(request, "Resend for channels other than SMS not supported")
            return
        send_sms(notification.person, notification.message)
