from django.db.models.query import QuerySet

from core.services import CRUDService
from events.models import Ticket
from notifications.utils import send_ticket_email
from payments.models import Payment
from payments.serilaizers import PaymentCreateSerializer, PaymentUpdateSerializer


class PaymentService(
    CRUDService[Payment, PaymentCreateSerializer, PaymentUpdateSerializer]
):
    def on_post_update(self, obj: Payment) -> None:
        tickets: QuerySet[Ticket] = Ticket.objects.filter(payment_id=obj.id)
        for ticket in tickets:
            send_ticket_email.apply_async(
                args=(ticket.id,),
                queue="main-queue",
            )


payment_service = PaymentService(Payment)
