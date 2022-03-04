from datetime import date, timedelta
from typing import Optional

from events.models import Event, TicketType
from partner.fixtures import partner_fixtures
from partner.models import Person


def event_fixture() -> dict:
    return {
        "name": "new-event",
        "poster": "media/42_EluV6G9.jpg",
        "event_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "event_location": "Nairobi",
        "description": "A random event description",
        "partner": str(partner_fixtures.create_partner_obj().id),
        "is_public": False,
        "event_state": "PR",
    }


def create_event_object(owner: Optional[Person] = None) -> Event:
    data = event_fixture()
    data["partner"] = partner_fixtures.create_partner_obj(owner=owner)
    event: Event = Event.objects.create(**data)
    event.save()
    return event


def ticket_type_fixture() -> dict:
    return {
        "name": "VIP",
        "price": 12000,
        "event": str(create_event_object().id),
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
        data["event"] = create_event_object(owner)
    else:
        data["event"] = event
    ticket_type: TicketType = TicketType.objects.create(**data)
    ticket_type.save()
    return ticket_type
