from datetime import date, timedelta
from typing import Sequence

from celery import shared_task
from django.db.models.query import QuerySet

from eticketing_api import settings
from events.models import ReminderOptIn, Ticket
from notifications.utils import send_sms
from partner.models import PartnerPromotion, PartnerSMS, PromoOptIn


@shared_task(name="send_out_reminders")
def send_out_reminders() -> None:

    next_day = date.today() + timedelta(days=1)

    ticket_filters = {
        "ticket_type__event__event_date__lte": next_day,
        "ticket_type__event__event_date__gte": date.today(),
    }

    tickets: QuerySet[Ticket] = Ticket.objects.filter(**ticket_filters).distinct(
        "payment__person_id"
    )

    for ticket in tickets:
        reminderoptin_filters = {
            "person_id": ticket.payment.person_id,
            "event_id": ticket.ticket_type.event.id,
        }
        reminder_set = ReminderOptIn.objects.filter(**reminderoptin_filters).count()
        try:
            event_partner_sms: PartnerSMS = PartnerSMS.objects.get(
                partner_id=ticket.ticket_type.event.partner.id
            )
        except PartnerSMS.DoesNotExist:
            continue

        if reminder_set and event_partner_sms.sms_left:
            send_sms.apply_async(
                args=(
                    ticket.payment.person_id,
                    settings.REMINDER_SMS.format(
                        ticket.payment.person.name, ticket.ticket_type.event.name
                    ),
                ),
                queue="main_queue",
            )


@shared_task(name="send_out_promos")
def send_out_promos() -> None:
    promos_: QuerySet[PartnerPromotion] = PartnerPromotion.objects.filter(verified=True)
    promos: Sequence[PartnerPromotion] = [
        promo for promo in promos_ if promo.next_run == date.today()
    ]

    for promo in promos:
        promo_optins: QuerySet[PromoOptIn] = PromoOptIn.objects.filter(
            partner_id=promo.partner.id
        ).distinct("person_id")
        for promo_optin in promo_optins:
            try:
                event_partner_sms: PartnerSMS = PartnerSMS.objects.get(
                    partner_id=promo_optin.partner.id
                )
            except PartnerSMS.DoesNotExist:
                continue
            if event_partner_sms.sms_left:
                send_sms.apply_async(
                    args=(
                        promo_optin.person_id,
                        promo.message,
                    ),
                    queue="main_queue",
                )
            promo.last_run = date.today()
            promo.save()
