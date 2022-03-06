from typing import Optional

from partner.fixtures import partner_fixtures
from partner.models import Person
from payments.constants import PaymentProviders
from payments.models import Payment


def payment_fixture(person_id: Optional[str] = None) -> dict:
    return {
        "amount": 10,
        "person_id": person_id
        if person_id
        else str(partner_fixtures.create_person_obj().id),
        "made_through": PaymentProviders.MPESA.value,
    }


def create_payment_object(person: Optional[Person] = None) -> Payment:
    payment_data = payment_fixture(person_id=str(person.id) if person else None)
    return Payment.objects.create(**payment_data)
