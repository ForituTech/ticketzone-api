from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorExceptionFA as HttpErrorException
from events.models import Event
from partner.utils import random_password
from partner_api.models import PaymentIntent, PaymentIntentTicketType
from partner_api.payments.serializers import (
    PaymentCreateSerializer,
    PaymentIntentCreateSerializer,
    TicketTypeInnerSerializer,
)
from payments.models import Payment
from payments.services import payment_service


class PaymentsService:
    def create_payment_intent(
        self, payment_in: PaymentIntentCreateSerializer
    ) -> PaymentIntent:
        payment_in_dict = payment_in.dict()
        payment_in_dict["person"]["hashed_password"] = random_password()
        obj_data = payment_service.validate_ticket_types_and_person(
            obj_data=payment_in_dict
        )
        intent = PaymentIntent.objects.create(
            amount=obj_data["amount"],
            person_id=obj_data["person_id"],
            callback_url=payment_in.callback_url,
        )
        intent.save()
        for ticket_type in payment_in.ticket_types:
            tt_intent = PaymentIntentTicketType.objects.create(
                payment_intent=intent,
                ticket_type_id=ticket_type.id,
                amount=ticket_type.amount,
            )
            tt_intent.save()

        return intent

    def get_payment_intent(self, intent_id: str) -> PaymentIntent:
        intent = PaymentIntent.objects.filter(pk=intent_id).first()
        if not intent:
            raise HttpErrorException(
                status_code=404, code=ErrorCodes.PAYMENT_INTENT_NOT_FOUND
            )

        return intent

    def get_related_event(self, intent_id: str) -> Event:
        intent = PaymentIntent.objects.filter(pk=intent_id).first()
        if not intent:
            raise HttpErrorException(
                status_code=404, code=ErrorCodes.PAYMENT_INTENT_NOT_FOUND
            )

        ticket_type = intent.ticket_type_rel.first()
        if not ticket_type:
            raise HttpErrorException(
                status_code=400,
                code=ErrorCodes.INTERGRATION_ERROR,
                extra="Intent doesn't have any ticket types",
            )

        return Event.objects.get(id=ticket_type.event_id)

    def create_payment_from_intent(self, payment: PaymentCreateSerializer) -> Payment:
        intent = self.get_payment_intent(intent_id=str(payment.intent_id))
        payment_data = {
            "amount": intent.amount,
            "person_id": str(intent.person_id),
            "made_through": payment.made_through.value,
        }
        payment_obj = Payment.objects.create(**payment_data)
        payment_obj.save()
        payment_data["ticket_types"] = [
            TicketTypeInnerSerializer.from_orm(ticket_type).dict()
            for ticket_type in intent.ticket_types
        ]
        payment_service.on_post_create(payment_obj, payment_data)

        return payment_obj


payments_service = PaymentsService()
