from typing import Optional

from events.models import Event, TicketType
from partner.fixtures import partner_fixtures

event_fixture = {
    "name": "new-event",
    "poster": "media/42_EluV6G9.jpg",
    "event_date": "2022-03-31",
    "event_location": "Nairobi",
    "description": "A random event description",
    "partner": "4c545373-d195-4e67-873b-24c7e6b580d0",
    "is_public": False,
    "event_state": "PR",
}

ticket_type_fixture = {
    "name": "VIP",
    "price": 12000,
    "event": "d46c26c2-370b-479c-a6db-c832c566707f",
    "active": True,
    "amsg": "Open Soon",
    "amount": 1200,
    "is_visible": False,
}


def create_event_object() -> Event:
    data = event_fixture.copy()
    data["partner"] = partner_fixtures.create_partner_obj()
    event: Event = Event.objects.create(**data)
    return event


def create_ticket_type_obj(event: Optional[Event] = None) -> TicketType:
    data = ticket_type_fixture.copy()
    if not event:
        data["event"] = create_event_object()
    else:
        data["event"] = event
    ticket_type: TicketType = TicketType.objects.create(**data)
    return ticket_type
