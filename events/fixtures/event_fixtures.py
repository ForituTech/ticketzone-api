from datetime import date, datetime, timedelta
from typing import Dict, Optional, Union

from events.models import (
    Event,
    EventCategory,
    EventPromotion,
    TicketPromotion,
    TicketType,
)
from partner.fixtures import partner_fixtures
from partner.models import Person


def event_category_fixture() -> Dict[str, str]:
    return {
        "name": "musical",
    }


def create_event_category_obj() -> EventCategory:
    return EventCategory.objects.create(**event_category_fixture())


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
        "time": (datetime.now() + timedelta(hours=4)).strftime("%H:%M:%S"),
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


def event_promo_fixture(event_id: Optional[str] = None) -> dict:
    return {
        "name": "10poff",
        "event_id": event_id if event_id else str(create_event_object().id),
        "promotion_rate": 10,
        "expiry": (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "use_limit": 10,
    }


def create_event_promo_obj(event: Optional[Event] = None) -> EventPromotion:
    data = event_promo_fixture(event_id=str(event.id) if event else None)
    return EventPromotion.objects.create(**data)


def ticket_promo_fixture(ticket_id: Optional[str] = None) -> dict:
    return {
        "name": "10poff",
        "ticket_id": ticket_id if ticket_id else str(create_ticket_type_obj().id),
        "promotion_rate": 10,
        "expiry": (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "use_limit": 10,
    }


def create_ticket_promo_obj(
    ticket_type: Optional[TicketType] = None,
) -> TicketPromotion:
    data = ticket_promo_fixture(ticket_id=str(ticket_type.id) if ticket_type else None)
    return TicketPromotion.objects.create(**data)
