from typing import Optional

from events.fixtures import event_fixtures
from events.models import TicketType
from payments.fixtures import payment_fixtures
from payments.models import Payment
from tickets.models import Ticket


def ticket_fixture(
    ticket_type_id: Optional[str] = None, payment_id: Optional[str] = None
) -> dict:
    return {
        "ticket_type_id": ticket_type_id
        if ticket_type_id
        else str(event_fixtures.create_ticket_type_obj().id),
        "payment_id": payment_id
        if payment_id
        else str(payment_fixtures.create_payment_object().id),
    }


def create_ticket_obj(
    ticket_type: Optional[TicketType] = None, payment: Optional[Payment] = None
) -> Ticket:
    ticket_data = ticket_fixture(
        ticket_type_id=str(ticket_type.id)
        if ticket_type
        else str(event_fixtures.create_ticket_type_obj().id),
        payment_id=str(payment.id)
        if payment
        else str(payment_fixtures.create_payment_object().id),
    )
    ticket = Ticket.objects.create(**ticket_data)
    ticket.save()
    return ticket
