from django.test import TestCase
from rest_framework.test import APIClient

from partner.fixtures import partner_fixtures


class PartnerTestCase(TestCase):
    fixtures = [
        "banking_info.json",
        "person.json",
        "partner.json",
        "events.json",
        "ticket_types.json",
    ]

    def setUp(self) -> None:
        auth_header = {"Authorization": partner_fixtures.create_auth_token()}
        self.authed_client = APIClient(**auth_header)
        self.unauthed_client = APIClient()

    def test_login__authed(self) -> None:
        login_credentials = {"phonenumber": "254799762765", "password": "123456"}
        res = self.authed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 202

    def test_login(self) -> None:
        login_credentials = {"phonenumber": "254799762765", "password": "123456"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 200
        assert "token" in res.json()

    def test_login__no_credentials(self) -> None:
        login_credentials = {"phonenumber": "254799762771", "password": "123456"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]

        login_credentials = {"phonenumber": "254799762765", "password": "123457"}
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]
