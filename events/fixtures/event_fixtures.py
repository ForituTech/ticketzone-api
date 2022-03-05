from datetime import date, timedelta
from typing import Optional, Union

from events.models import Event, TicketType
from partner.fixtures import partner_fixtures
from partner.models import Person


def event_fixture(partner_id: Union[str, int] = None) -> dict:
    return {
        "name": "new-event",
        "poster": "media/42_EluV6G9.jpg",
        "event_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "event_location": "Nairobi",
        "description": "A random event description",
        "partner_id": partner_id
        if partner_id
        else str(partner_fixtures.create_partner_obj().id),
        "is_public": False,
        "event_state": "PR",
    }


def create_event_object(owner: Optional[Person] = None) -> Event:
    data = event_fixture()
    data["partner_id"] = partner_fixtures.create_partner_obj(owner=owner).id
    event: Event = Event.objects.create(**data)
    event.save()
    return event


def ticket_type_fixture(event_id: Union[str, int] = None) -> dict:
    return {
        "name": "VIP",
        "price": 12000,
        "event_id": event_id if event_id else str(create_event_object().id),
        "active": True,
        "amsg": "Open Soon",
        "amount": 1200,
        "is_visible": False,
    }


def create_ticket_type_obj(
    event: Optional[Event] = None, owner: Optional[Person] = None
) -> TicketType:
    data = ticket_type_fixture()
    if not event:
        data["event_id"] = create_event_object(owner).id
    else:
        data["event_id"] = event.id
    ticket_type: TicketType = TicketType.objects.create(**data)
    ticket_type.save()
    return ticket_type
