from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Sequence

from celery import shared_task
from django.contrib import admin, messages
from django.core.mail import EmailMessage
from django.db.models.query import QuerySet
from django.http import HttpRequest

from eticketing_api import settings
from eticketing_api.celery import celery
from events.models import Ticket
from notifications.constants import NotificationsChannels
from notifications.models import Notification
from notifications.pusher import pusher_client
from notifications.sms import sms_client
from partner.models import Person
from tickets.utils import generate_ticket_pdf


@celery.task(name=__name__ + ".send_email")
def send_email(
    person_id: str,
    header: str,
    body: str,
    html: bool = False,
    retry: int = 0,
) -> bool:
    person: Person = Person.objects.get(pk=person_id)
    email = EmailMessage(
        subject=settings.TICKET_EMAIL_TITLE,
        to=(person.email,),
        body=body,
    )
    email.content_subtype = "html"
    sent = email.send(fail_silently=True)
    if not sent and retry < 5:
        send_email(person_id, header, body, html, retry=retry + 1)
        return False
    Notification.objects.create(
        person=person,
        channel=NotificationsChannels.EMAIL.value,
        has_data=False,
        sent=bool(sent),
    )
    return bool(sent)


@celery.task(name=__name__ + ".send_multi_email")
def send_multi_email(
    persons: List[Person],
    header: str,
    body: str,
    attachments: Sequence[Any] = [],
    html: bool = False,
    retry: int = 0,
) -> bool:
    if retry == 5:
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


@celery.task(name=__name__ + ".send_ticket_email")
def send_ticket_email(
    ticket_id: str, body_source: str = settings.DEFAULT_TICKET_TEMPLATE, retry: int = 0
) -> bool:
    if retry == 5:
        return False
    ticket: Ticket = Ticket.objects.get(pk=ticket_id)
    ticket_pdf = generate_ticket_pdf(ticket)
    ticket_pdf.seek(0)
    email = EmailMessage(
        subject=settings.TICKET_EMAIL_TITLE,
        to=(ticket.payment.person.email,),
        attachments=[(ticket.__str__(), ticket_pdf.read(), "application/pdf")],
        body=settings.TICKET_EMAIL_BODY.format(ticket.payment.person.name),
    )
    email.content_subtype = "html"
    sent = email.send(fail_silently=True)
    if not sent:
        send_ticket_email.apply_async(
            args=(
                ticket_id,
                body_source,
                retry + 1,
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )
    if not retry:
        Notification.objects.create(
            person=ticket.payment.person,
            channel=NotificationsChannels.EMAIL.value,
            has_data=True,
        )
        ticket.sent = True
        ticket.save()
    else:
        retry -= 1
    return True


@celery.task(name=__name__ + ".send_push_notification")
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


@celery.task(name=__name__ + ".send_sms")
def send_sms(person_id: str, message: str) -> None:
    person: Person = Person.objects.get(pk=person_id)
    notification: Notification = Notification.objects.create(
        person=person,
        message=message,
        channel=NotificationsChannels.SMS.value,
        has_data=False,
    )
    sms_client.send(message, [person.phone_number])
    notification.sent = True
    notification.save()


@celery.task(name=__name__ + ".resend_notification")
@admin.action(description="Resend Notification")
def resend_notification(
    modeladmin: Any, request: HttpRequest, queryset: QuerySet[Notification]
) -> None:
    for notification in queryset:
        if notification.channel != NotificationsChannels.SMS.value:
            messages.error(request, "Resend for channels other than SMS not supported")
            return
        send_sms(notification.person, notification.message)


@shared_task(name="cleanup_notifications")
def cleanup_notifications() -> None:
    last_week = date.today() - timedelta(weeks=1)
    notifications: QuerySet[Notification] = Notification.objects.filter(
        created_at__lte=last_week
    )
    for notification in notifications:
        notification.delete()
