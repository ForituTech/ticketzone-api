from partner.utils import random_password
from partner_api.models import PaymentIntent, PaymentIntentTicketType
from partner_api.payments.serializers import PaymentIntentCreateSerializer
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
        for ticket_type in obj_data.get("tt_objs", None):
            tt_intent = PaymentIntentTicketType.objects.create(
                payment_intent=intent, ticket_type=ticket_type
            )
            tt_intent.save()

        return intent


payments_service = PaymentsService()
