from typing import Optional

from partner.fixtures import partner_fixtures
from partner.models import Person
from payments.constants import PaymentProviders
from payments.models import Payment


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
