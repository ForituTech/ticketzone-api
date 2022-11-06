from datetime import date, datetime, timedelta
from typing import Dict, Optional, Union

from core.utils import random_string
from events.models import (
    Event,
    EventCategory,
    EventPromotion,
    PartnerPersonSchedule,
    TicketPromotion,
    TicketType,
)
from partner.fixtures import partner_fixtures
from partner.models import Person


def event_category_fixture() -> Dict[str, str]:
    return {
        "name": random_string(),
    }


def create_event_category_obj() -> EventCategory:
    return EventCategory.objects.create(**event_category_fixture())


def event_fixture(
    partner_id: Union[str, int] = None, category_id: Optional[str] = None
) -> dict:
    return {
        "name": random_string(),
        "poster": open("media/42_EluV6G9.jpg", "rb"),
        "event_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "event_end_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "event_location": "Nairobi",
        "description": random_string(),
        "partner_id": partner_id
        if partner_id
        else str(partner_fixtures.create_partner_obj().id),
        "is_public": False,
        "event_state": "PR",
        "time": (datetime.now() + timedelta(hours=4)).strftime("%H:%M:%S"),
        "end_time": (datetime.now() + timedelta(days=1)).strftime("%H:%M:%S"),
        "category_id": category_id or str(create_event_category_obj().id),
    }


def create_event_object(
    owner: Optional[Person] = None,
    state: Optional[str] = "PR",
    category_id: Optional[str] = None,
) -> Event:
    data = event_fixture(category_id=category_id)
    data["partner_id"] = partner_fixtures.create_partner_obj(owner=owner).id
    data["poster"] = "media/42_EluV6G9.jpg"
    data["event_state"] = state
    event: Event = Event.objects.create(**data)
    event.save()
    return event


def ticket_type_fixture(event_id: Union[str, int] = None, use_limit: int = 1) -> dict:
    return {
        "name": random_string(),
        "price": 12000,
        "event_id": event_id if event_id else str(create_event_object().id),
        "active": True,
        "amsg": random_string(),
        "amount": 1200,
        "is_visible": False,
        "use_limit": use_limit,
    }


def ticket_type_min_fixture(use_limit: int = 1) -> dict:
    return {
        "name": random_string(),
        "price": 12000,
        "active": True,
        "amsg": random_string(),
        "amount": 1200,
    }


def create_ticket_type_obj(
    event: Optional[Event] = None, owner: Optional[Person] = None, use_limit: int = 1
) -> TicketType:
    data = ticket_type_fixture(use_limit=use_limit)
    if not event:
        data["event_id"] = create_event_object(owner).id
    else:
        data["event_id"] = event.id
    ticket_type: TicketType = TicketType.objects.create(**data)
    ticket_type.save()
    return ticket_type


def event_promo_fixture(event_id: Optional[str] = None) -> dict:
    return {
        "name": random_string(),
        "event_id": event_id if event_id else str(create_event_object().id),
        "promotion_rate": 10,
        "expiry": (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "use_limit": 10,
    }


def event_promo_min_fixture() -> dict:
    return {
        "name": random_string(),
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


def partner_person_schedule_fixture(
    event_id: Optional[str] = None, partner_person_id: Optional[str] = None
) -> dict:
    return {
        "event_id": event_id or create_event_object().id,
        "partner_person_id": partner_person_id
        or partner_fixtures.create_partner_person().id,
    }


def create_partner_person_schedule(
    event_id: Optional[str] = None, partner_person_id: Optional[str] = None
) -> PartnerPersonSchedule:
    try:
        schedule: PartnerPersonSchedule = PartnerPersonSchedule.objects.get(
            partner_person_id=partner_person_id  # type: ignore
        )
        event_id = event_id if event_id else str(create_event_object().id)
        schedule.event_id = event_id
        schedule.save()
        return schedule
    except PartnerPersonSchedule.DoesNotExist:
        return PartnerPersonSchedule.objects.create(
            **partner_person_schedule_fixture(event_id, partner_person_id)
        )
