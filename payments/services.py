from http import HTTPStatus
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models.query import QuerySet

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from eticketing_api import settings
from events.models import Ticket, TicketType
from events.services import event_promo_service
from notifications.tasks import send_ticket_email
from partner.models import PartnerSMS
from partner.services import partner_service, partner_sms_service, person_service
from payments.configs import payment_processor_map
from payments.constants import CONFIRMED_PAYMENT_STATES
from payments.models import Payment, PaymentMethod
from payments.serilaizers import (
    PaymentCreateSerializerInner,
    PaymentMethodWriteSerializer,
    PaymentUpdateSerializer,
    SMSPaymentCreateSerializerInner,
)
from tickets.serializers import TicketCreateSerializer
from tickets.services import ticket_service


class PaymentService(
    CRUDService[Payment, PaymentCreateSerializerInner, PaymentUpdateSerializer]
):
    def validate_ticket_types_and_person(
        self, obj_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        amount = 0
        event_id: Optional[str] = ""
        ticket_type_objs: List[TicketType] = []
        if ticket_types := obj_data.get("ticket_types", None):
            for ticket_type in ticket_types:
                if ticket_type_obj := TicketType.objects.filter(
                    id=ticket_type["id"], active=True
                ).first():
                    amount += round((ticket_type_obj.price * ticket_type["amount"]), 2)
                    if event_id == "":
                        event_id = str(ticket_type_obj.event_id)
                    if event_id != str(ticket_type_obj.event_id):
                        raise HttpErrorException(
                            status_code=400,
                            code=ErrorCodes.NOT_SUPPORTED,
                            extra="Ticket bundling from multiple events is not supported",
                        )
                    if ticket_type_obj.amount == 0:
                        raise HttpErrorException(
                            status_code=400,
                            code=ErrorCodes.TICKET_TYPE_SOLD_OUT,
                            extra=ticket_type_obj.name,
                        )
                    if ticket_type_obj.amount < ticket_type["amount"]:
                        ticket_type_obj.refresh_from_db()
                        raise HttpErrorException(
                            status_code=400,
                            code=ErrorCodes.TICKET_TYPE_INSUFFICIENT,
                            extra=(
                                f"The ticket {ticket_type_obj.name} has"
                                f" only {ticket_type_obj.amount} left"
                            ),
                        )
                    ticket_type_objs.append(ticket_type_obj)

                else:
                    raise HttpErrorException(
                        status_code=400,
                        code=ErrorCodes.INTERGRATION_ERROR,
                        extra=f"Invalid Ticket Type id {ticket_type['id']}",
                    )
            obj_data["amount"] = amount
            obj_data["tt_objs"] = ticket_type_objs

        if person := obj_data.get("person", None):
            obj_data["person_id"] = str(person_service.get_or_create(person).id)
            del obj_data["person"]

        if promo := obj_data.get("promo", None):
            if promo_obj := event_promo_service.get(id=promo, event_id=event_id):
                amount = (
                    amount
                    * round((100 - promo_obj.promotion_rate) / 100, 2)  # type: ignore
                    if amount
                    else 0
                )
                obj_data["amount"] = amount
            else:
                raise HttpErrorException(
                    status_code=404, code=ErrorCodes.PROMO_NOT_FOUND
                )

        return obj_data

    def on_post_create(self, obj: Payment, obj_in: Dict[str, Any]) -> None:
        for ticket_type in obj_in["ticket_types"]:
            ticket_service.create(
                obj_data={
                    "ticket_type_id": ticket_type["id"],
                    "payment_id": str(obj.id),
                },
                serializer=TicketCreateSerializer,
            )

            # decrement the relevant ticket_types uses
            # whether or not these exist has already been validated
            with transaction.atomic():
                ticket_type_obj = TicketType.objects.select_for_update().get(
                    id=ticket_type["id"]
                )
                ticket_type_obj.amount -= ticket_type["amount"]
                ticket_type_obj.save()

            if processor := payment_processor_map.get(obj.made_through, None):
                processor.c2b_receive(payment=obj)
            else:
                raise HttpErrorException(
                    status_code=503, code=ErrorCodes.PROVIDER_NOT_SUPPORTED
                )

    def on_post_update(self, obj: Payment) -> None:
        if obj.state in CONFIRMED_PAYMENT_STATES:
            obj.verified = True
            obj.save()
            tickets: QuerySet[Ticket] = Ticket.objects.filter(payment_id=obj.id)
            for ticket in tickets:
                send_ticket_email.apply_async(
                    args=(ticket.id,),
                    queue=settings.CELERY_MAIN_QUEUE,
                )

    def fund_sms_package(
        self, partner_id: str, payment_in: SMSPaymentCreateSerializerInner
    ) -> PartnerSMS:
        partner = partner_service.get(id=partner_id)
        if not partner:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_PARTNER_ID
            )
        sms_package = partner_sms_service.get_latest_sms_package(partner_id=partner_id)

        if processor := payment_processor_map.get(payment_in.made_through, None):  # type: ignore
            state = processor.b2b_recieve(amount=payment_in.amount, partner=partner)
        else:
            raise HttpErrorException(
                status_code=503, code=ErrorCodes.PROVIDER_NOT_SUPPORTED
            )

        if state.value in CONFIRMED_PAYMENT_STATES:
            credited_sms = int(payment_in.amount / sms_package.per_sms_rate)  # type: ignore
            with transaction.atomic():
                sms_package.sms_limit += credited_sms
                sms_package.save()

        return sms_package


payment_service = PaymentService(Payment)


class PaymentMethodService(
    CRUDService[
        PaymentMethod, PaymentMethodWriteSerializer, PaymentMethodWriteSerializer
    ]
):
    pass


payment_method_service = PaymentMethodService(PaymentMethod)
