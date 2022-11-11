from typing import Any, Dict, List, Optional

from events.tests import event_fixtures
from partner.fixtures import partner_fixtures
from partner.models import Person
from payments.constants import PaymentProviders
from payments.models import Payment, PaymentMethod


def payment_fixture(
    person_id: Optional[str] = None, amount: Optional[float] = 10.0
) -> dict:
    return {
        "amount": amount,
        "person_id": person_id
        if person_id
        else str(partner_fixtures.create_person_obj().id),
        "made_through": PaymentProviders.MPESA.value,
    }


def create_payment_object(
    person: Optional[Person] = None, amount: Optional[float] = 10.0
) -> Payment:
    payment_data = payment_fixture(
        person_id=str(person.id) if person else None, amount=amount
    )
    return Payment.objects.create(**payment_data)


def ticket_type_fixture(amount: int = 2) -> dict:
    return {
        "id": str(event_fixtures.create_ticket_type_obj().id),
        "amount": amount,
    }


def person_fixture_from_person_obj(person: Person) -> dict:
    return {
        "name": person.name,
        "email": person.email,
        "phone_number": person.phone_number,
    }


def payment_create_fixture(
    amount: int = 2,
    person: Optional[Person] = None,
    ticket_types: Optional[List[Dict[str, Any]]] = None,
) -> dict:
    return {
        "person": person_fixture_from_person_obj(person)
        if person
        else partner_fixtures.person_fixture_no_password(),
        "ticket_types": ticket_types or [ticket_type_fixture(amount)],
        "made_through": PaymentProviders.MPESA.value,
    }


def create_payment_method_obj(
    name: str = PaymentProviders.MPESA.value, poster: Optional[str] = None
) -> PaymentMethod:
    return PaymentMethod.objects.create(name=name, poster=poster)
