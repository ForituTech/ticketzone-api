from django.test import TestCase
from rest_framework.test import APIClient

from eticketing_api import settings
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from payments.fixtures import payment_fixtures


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
        payment_data = payment_fixtures.payment_fixture(
            person_id=str(self.owner.person_id)
        )
        res = self.client.post("/payments/", data=payment_data, format="json")

        assert res.status_code == 200
        assert res.json()["person_id"] == payment_data["person_id"]

    def test_create_payment__non_self(self) -> None:
        payment_data = payment_fixtures.payment_fixture()
        res = self.client.post("/payments/", data=payment_data, format="json")

        assert res.status_code == 403

    def test_create_payment__not_logged_in(self) -> None:
        payment_data = payment_fixtures.payment_fixture()
        res = self.unauthed_client.post("/payments/", data=payment_data, format="json")

        assert res.status_code == 403
