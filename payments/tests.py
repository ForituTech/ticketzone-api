import uuid

from django.test import TestCase
from rest_framework.test import APIClient

from eticketing_api import settings
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from payments.fixtures import payment_fixtures

API_VER = settings.API_VERSION_STRING


class PaymentTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_access_token(
                self.owner.person
            )
        }
        self.client = APIClient(False, **auth_header)
        self.unauthed_client = APIClient(
            False,
        )

    def test_create_payment(self) -> None:
        payment_data = payment_fixtures.payment_create_fixture(person=self.owner.person)

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 200
        assert res.json()["person_id"] == str(self.owner.person.id)

    def test_create_payment__inavlid_ticket_type(self) -> None:
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[{"id": uuid.uuid4(), "amount": 1}],
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 400

    def test_list_payment_methods(self) -> None:
        payment_method = payment_fixtures.create_payment_method_obj()

        res = self.client.get(f"/{API_VER}/payments/methods/", format="json")

        assert res.status_code == 200
        returned_payment_method_names = [method["name"] for method in res.json()]
        assert payment_method.name in returned_payment_method_names
