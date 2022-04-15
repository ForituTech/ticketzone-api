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

    def redeem(self, pk: str) -> Ticket:
        try:
            ticket: Ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_TICKET_ID
            )
        if ticket.payment.state != PaymentStates.PAID.value:
            raise HttpErrorException(
                status_code=HTTPStatus.FORBIDDEN,
                code=ErrorCodes.UNPAID_FOR_TICKET,
            )
        if ticket.ticket_type.use_limit <= ticket.uses:
            raise HttpErrorException(
                status_code=HTTPStatus.FORBIDDEN,
                code=ErrorCodes.REDEEMED_TICKET,
            )

        ticket.uses += 1

        ticket.save()
        return ticket

    def send(self, ticket: Ticket) -> bool:
        pass


ticket_service = TicketService(Ticket)
