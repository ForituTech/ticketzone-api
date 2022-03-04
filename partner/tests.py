from django.test import TestCase
from rest_framework.test import APIClient

from partner.constants import PersonType
from partner.fixtures import partner_fixtures


class PartnerTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        auth_header = {
            "Authorization": partner_fixtures.create_auth_token(self.owner.person)
        }
        self.authed_client = APIClient(**auth_header)
        self.unauthed_client = APIClient()

    def tearDown(self) -> None:
        self.owner.person.delete()

    def test_login__authed(self) -> None:
        login_credentials = {"phone_number": "254799762765", "password": "123456"}
        res = self.authed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 202

    def test_login(self) -> None:
        login_credentials = {"phone_number": "254799762765", "password": "123456"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 200
        assert "token" in res.json()

    def test_login__no_credentials(self) -> None:
        login_credentials = {"phone_number": "254799762771", "password": "123456"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]

        login_credentials = {"phone_number": "254799762765", "password": "123457"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]
