from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models.query import QuerySet

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from eticketing_api import settings
from events.models import Ticket, TicketType
from events.services import event_promo_service
from notifications.utils import send_ticket_email
from partner.services import person_service
from payments.constants import CONFIRMED_PAYMENT_STATES
from payments.models import Payment, PaymentMethod
from payments.serilaizers import (
    PaymentCreateSerializerInner,
    PaymentMethodWriteSerializer,
    PaymentUpdateSerializer,
)
from tickets.serializers import TicketCreateSerializer
from tickets.services import ticket_service


class PaymentService(
    CRUDService[Payment, PaymentCreateSerializerInner, PaymentUpdateSerializer]
):
    @staticmethod
    def validate_ticket_types_and_person(obj_data: Dict[str, Any]) -> Dict[str, Any]:
        amount = 0
        event_id: Optional[str] = ""
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

                else:
                    raise HttpErrorException(
                        status_code=400,
                        code=ErrorCodes.INTERGRATION_ERROR,
                        extra=f"Invalid Ticket Type id {ticket_type['id']}",
                    )
            obj_data["amount"] = amount

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

    def on_post_update(self, obj: Payment) -> None:
        if obj.state in CONFIRMED_PAYMENT_STATES:
            tickets: QuerySet[Ticket] = Ticket.objects.filter(payment_id=obj.id)
            for ticket in tickets:
                send_ticket_email.apply_async(
                    args=(ticket.id,),
                    queue=settings.CELERY_MAIN_QUEUE,
                )


payment_service = PaymentService(Payment)


class PaymentMethodService(
    CRUDService[
        PaymentMethod, PaymentMethodWriteSerializer, PaymentMethodWriteSerializer
    ]
):
    pass


payment_method_service = PaymentMethodService(PaymentMethod)
