from datetime import date, timedelta
from typing import Sequence

from celery import shared_task
from django.db.models.query import QuerySet

from eticketing_api import settings
from events.models import ReminderOptIn, Ticket
from notifications.tasks import send_sms
from owners.models import Owner
from partner.models import Partner, PartnerPromotion, PartnerSMS, PromoOptIn
from partner.services import partner_service


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
                queue=settings.CELERY_NOTIFICATIONS_QUEUE,
            )
            event_partner_sms.sms_used += 1
            event_partner_sms.save()


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
                break
            if event_partner_sms.sms_left:
                send_sms.apply_async(
                    args=(
                        promo_optin.person_id,
                        promo.message,
                    ),
                    queue=settings.CELERY_NOTIFICATIONS_QUEUE,
                )
                event_partner_sms.sms_used += 1
                event_partner_sms.save()

            promo.last_run = date.today()
            promo.save()


@shared_task(name="reconcile_payments")
def reconcile_payments() -> None:
    partners: QuerySet[Partner] = Partner.objects.all()

    total_balance = 0.0
    for partner in partners:
        partner_balance = partner_service.balance(str(partner.id))
        send_sms.apply_async(
            args=(
                partner.owner.phone_number,
                settings.POST_RECONCILIATION_MESSAGE.format(
                    partner.owner.name, partner_balance
                ),
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )
        if partner_balance > 0:
            # TODO: Add payment provider send to partner
            total_balance += partner_balance * (partner.comission_rate / 100)
        else:
            total_balance += partner_balance

    owners: QuerySet[Owner] = Owner.objects.all()
    for owner in owners:
        send_sms.apply_async(
            args=(
                owner.phone_number,
                f"Your weekly leverage for {date.today()} "
                f"is {total_balance*(owner.stake/100)}",
            ),
            queue=settings.CELERY_NOTIFICATIONS_QUEUE,
        )
