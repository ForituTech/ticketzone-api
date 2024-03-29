from typing import Any, Dict, Optional

from events.fixtures import event_fixtures
from events.models import Event, TicketScan, TicketType
from partner.fixtures.partner_fixtures import create_partner_person
from partner.models import Partner, Person
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
    ticket_type: Optional[TicketType] = None,
    payment: Optional[Payment] = None,
    event: Optional[Event] = None,
    person: Optional[Person] = None,
) -> Ticket:
    ticket_data = ticket_fixture(
        ticket_type_id=str(ticket_type.id)
        if ticket_type
        else str(event_fixtures.create_ticket_type_obj(event=event).id),
        payment_id=str(payment.id)
        if payment
        else str(payment_fixtures.create_payment_object(person=person).id),
    )
    ticket: Ticket = Ticket.objects.create(**ticket_data)
    ticket.save()
    return ticket


def ticket_scan_fixture(
    agent_id: Optional[str] = None,
    ticket_id: Optional[str] = None,
    partner: Optional[Partner] = None,
    person: Optional[Person] = None,
) -> Dict[str, Any]:
    return {
        "agent_id": agent_id
        or str(create_partner_person(partner=partner, person=person).id),
        "ticket_id": ticket_id or str(create_ticket_obj().id),
    }


def create_ticket_scan_obj(
    agent_id: Optional[str] = None,
    ticket_id: Optional[str] = None,
    partner: Optional[Partner] = None,
    person: Optional[Person] = None,
) -> TicketScan:
    return TicketScan.objects.create(
        **ticket_scan_fixture(agent_id, ticket_id, partner, person)
    )
