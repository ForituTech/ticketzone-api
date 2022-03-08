from http import HTTPStatus

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from payments.constants import PaymentStates
from tickets.models import Ticket
from tickets.serializers import TicketCreateSerializer, TicketUpdateInnerSerializer
from tickets.utils import compute_ticket_hash


class TicketService(
    CRUDService[Ticket, TicketCreateSerializer, TicketUpdateInnerSerializer]
):
    def on_post_create(self, obj: Ticket) -> None:
        hash = compute_ticket_hash(obj)
        try:
            Ticket.objects.get(hash=hash)
            self.on_post_create(obj)
        except Ticket.DoesNotExist:
            obj.hash = hash
            obj.save()

    def on_pre_update(self, obj_in: TicketUpdateInnerSerializer, obj: Ticket) -> None:
        if obj.payment.state != PaymentStates.PAID.value:
            raise HttpErrorException(
                status_code=HTTPStatus.FORBIDDEN,
                code=ErrorCodes.UNPAID_FOR_TICKET,
            )

    def send(self, ticket: Ticket) -> bool:
        pass


ticket_service = TicketService(Ticket)
