from datetime import date, timedelta
from random import randint
from typing import Dict, Optional

from core.utils import random_string
from events.fixtures import event_fixtures
from events.models import Event, ReminderOptIn
from partner.constants import PartnerPromotionPeriod, PersonType
from partner.models import (
    Partner,
    PartnerPerson,
    PartnerPromotion,
    PartnerSMS,
    Person,
    PromoOptIn,
)
from partner.serializers import PersonCreateSerializer
from partner.services import person_service
from partner.utils import create_access_token, random_password


def random_phone_number() -> str:
    base = 254700000000
    return str(base + randint(1, 99999999))


def person_fixture(password: Optional[str] = None) -> dict:
    return {
        "name": random_string(),
        "email": f"{random_string()[:5]}@{random_string()[:4]}.com",
        "phone_number": f"+{random_phone_number()}",
        "hashed_password": password or random_password(),
    }


def person_fixture_no_password() -> dict:
    return {
        "name": random_string(),
        "email": f"{random_string()[:5]}@{random_string()[:4]}.com",
        "phone_number": f"+{random_phone_number()}",
    }


partner_banking_info_fixture = {
    "bank_code": random_string(),
    "bank_account_number": random_string(),
}


def create_person_obj(password: Optional[str] = None) -> Person:
    person_data = person_fixture(password=password)
    try:
        person: Person = Person.objects.get(phone_number=person_data["phone_number"])
    except Person.DoesNotExist:
        person = person_service.create(
            obj_data=person_data, serializer=PersonCreateSerializer
        )
    person.save()
    return person


def create_auth_token(person: Optional[Person] = None) -> str:
    if not person:
        person = create_person_obj()
    person.save()
    return create_access_token(person)


def partner_fixture(owner_id: Optional[str] = None) -> dict:
    return {
        "name": random_string(),
        "owner_id": owner_id if owner_id else str(create_person_obj().id),
        "verified": True,
        **partner_banking_info_fixture,
    }


def partner_fixture_with_owner_data() -> dict:
    return {
        "name": random_string(),
        "owner": person_fixture(),
        "bank_code": random_string(),
        "bank_account_number": random_string(),
    }


def create_partner_obj(owner: Optional[Person] = None) -> Partner:
    data = partner_fixture(owner_id=str(owner.id) if owner else None)
    if not owner:
        owner = create_person_obj()
    data["owner_id"] = owner.id
    try:
        partner: Partner = Partner.objects.get(owner__id=owner.id)
    except Partner.DoesNotExist:
        partner = Partner.objects.create(**data)
    partner.save()
    return partner


def partner_person_fixture(
    person_type: PersonType = PersonType.TICKETING_AGENT,
) -> dict:
    return {
        "partner_id": str(create_partner_obj().id),
        "person": person_fixture(),
        "person_type": person_type.value,
    }


def create_partner_person(
    *,
    person: Optional[Person] = None,
    partner: Optional[Partner] = None,
    person_type: Optional[PersonType] = PersonType.PARTNER_MEMBER,
) -> PartnerPerson:
    if not person:
        person = create_person_obj()
    if not partner:
        if person_type == PersonType.OWNER:
            partner = create_partner_obj(owner=person)
        else:
            partner = create_partner_obj()
    partner_person: PartnerPerson = PartnerPerson.objects.create(
        person=person,
        partner=partner,
        person_type=person_type,
    )  # type: ignore
    partner_person.save()
    return partner_person


def reminder_optin_fixture(
    person_id: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Dict:
    return {
        "person_id": person_id if person_id else str(create_person_obj().id),
        "event_id": event_id
        if event_id
        else str(event_fixtures.create_event_object().id),
    }


def create_reminder_optin_object(
    person: Optional[Person] = None,
    event: Optional[Event] = None,
) -> ReminderOptIn:
    data = reminder_optin_fixture(
        person_id=str(person.id) if person else None,
        event_id=str(event.id) if event else None,
    )
    return ReminderOptIn.objects.create(**data)


def partner_sms_fixture(
    partner_id: Optional[str] = None, verified: bool = True
) -> Dict:
    return {
        "partner_id": partner_id if partner_id else str(create_partner_obj().id),
        "per_sms_rate": 10,
        "sms_limit": 10,
        "verified": verified,
    }


def create_partner_sms_obj(
    partner: Optional[Partner] = None, verified: bool = True
) -> PartnerSMS:
    data = partner_sms_fixture(
        partner_id=str(partner.id) if partner else None, verified=verified
    )
    return PartnerSMS.objects.create(**data)


def partner_promo_fixture(
    partner_id: Optional[str] = None,
    owner: Optional[Person] = None,
    repeat: Optional[PartnerPromotionPeriod] = PartnerPromotionPeriod.SINGLE_RUN,
    starts_on: date = date.today(),
    stops_on: date = date.today() + timedelta(days=1),
    verified: bool = True,
) -> Dict:
    return {
        "name": random_string(),
        "partner_id": partner_id if partner_id else str(create_partner_obj(owner).id),
        "repeat": repeat,
        "message": random_string(),
        "starts_on": starts_on,
        "stops_on": stops_on,
        "verified": verified,
    }


def create_partner_promo_obj(
    partner: Optional[Partner] = None,
    owner: Optional[Person] = None,
    repeat: Optional[PartnerPromotionPeriod] = PartnerPromotionPeriod.SINGLE_RUN,
    starts_on: date = date.today(),
    stops_on: date = date.today() + timedelta(days=1),
    verified: bool = True,
) -> PartnerPromotion:
    data = partner_promo_fixture(
        partner_id=str(partner.id) if partner else None,
        owner=owner,
        repeat=repeat,
        starts_on=starts_on,
        stops_on=stops_on,
        verified=verified,
    )
    return PartnerPromotion.objects.create(**data)


def partner_promo_optin_fixture(
    person_id: Optional[str] = None, partner_id: Optional[str] = None
) -> Dict:
    return {
        "person_id": person_id if person_id else str(create_person_obj().id),
        "partner_id": partner_id if partner_id else str(create_partner_obj().id),
    }


def create_partner_promo_optin_obj(
    person: Optional[Person] = None, partner: Optional[Partner] = None
) -> PromoOptIn:
    data = partner_promo_optin_fixture(
        person_id=str(person.id) if person else None,
        partner_id=str(partner.id) if partner else None,
    )
    return PromoOptIn.objects.create(**data)


def get_partner_owner_auth(partner: Partner) -> str:
    return create_access_token(partner.owner)
