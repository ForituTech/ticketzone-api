from typing import Optional

from partner.constants import PersonType
from partner.models import Partner, PartnerBankingInfo, PartnerPerson, Person
from partner.utils import create_access_token

person_fixture = {
    "name": "Nelson Mongare",
    "email": "nelsonmongare@protonmail.com",
    "phone_number": "254799762765",
    "hashed_password": "$2b$12$IjyvmhueX4ebK0WOElWvJODwy9zWfqSZDhul/BF8l7cVGahv/WYo6",
}

partner_banking_info_fixture = {
    "bank_code": 123456,
    "bank_account_number": 1234567891234657899,
}


def create_person_obj() -> Person:
    person_data = person_fixture.copy()
    try:
        person: Person = Person.objects.get(phone_number=person_data["phone_number"])
    except Person.DoesNotExist:
        person = Person.objects.create(**person_data)
    person.save()
    return person


def create_auth_token(person: Optional[Person] = None) -> str:
    if not person:
        person = create_person_obj()
    person.save()
    return create_access_token(person)


def create_banking_info_obj() -> PartnerBankingInfo:
    banking_info: PartnerBankingInfo = PartnerBankingInfo.objects.create(
        **partner_banking_info_fixture
    )
    banking_info.save()
    return banking_info


def partner_fixture() -> dict:
    return {
        "name": "Muze Ticketing",
        "owner": str(create_person_obj().id),
        "banking_info": str(create_banking_info_obj().id),
    }


def create_partner_obj(owner: Optional[Person] = None) -> Partner:
    data = partner_fixture()
    data["banking_info"] = create_banking_info_obj()
    if not owner:
        owner = create_person_obj()
    data["owner"] = owner
    try:
        partner: Partner = Partner.objects.get(owner__id=owner.id)
    except Partner.DoesNotExist:
        partner = Partner.objects.create(**data)
    partner.save()
    return partner


def create_partner_person(
    *,
    person: Optional[Person] = None,
    partner: Optional[Partner] = None,
    person_type: Optional[PersonType] = PersonType.PARTNER_MEMBER,
) -> PartnerPerson:
    partner_person: PartnerPerson = PartnerPerson.objects.create(
        person=person if person else create_person_obj(),
        partner=partner if partner else create_partner_obj(),
        person_type=person_type,
    )
    partner_person.save()
    return partner_person
