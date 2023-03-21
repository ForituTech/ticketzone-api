from django.test import TransactionTestCase
from fastapi.testclient import TestClient

from eticketing_api import settings
from eticketing_api.asgi import app
from events.fixtures.event_fixtures import create_event_object, create_ticket_type_obj
from partner.fixtures.partner_fixtures import create_partner_obj, person_fixture
from partner_api.auth.tests.fixtures import create_partner_api_credentials_obj
from partner_api.auth.utils import create_auth_token

API_BASE_URL = "/v1/payments"


class AuthTestCase(TransactionTestCase):
    def setUp(self) -> None:
        # fastapi client
        self.partner = create_partner_obj()
        self.api_credentials = create_partner_api_credentials_obj(self.partner)
        self.token = create_auth_token(api_creds=self.api_credentials)
        self.fa_client = TestClient(
            app, headers={settings.EXTERNAL_API_AUTH_HEADER: self.token["access_token"]}
        )

    def test_create_payment_intent(self) -> None:
        event = create_event_object(owner=self.partner.owner)
        ticket_types = [
            create_ticket_type_obj(event=event),
            create_ticket_type_obj(event=event),
            create_ticket_type_obj(event=event),
        ]
        person_data = person_fixture()
        ticket_type_data = [
            {"id": str(ticket_type.id), "amount": 1} for ticket_type in ticket_types
        ]
        intent = {
            "person": person_data,
            "ticket_types": ticket_type_data,
            "callback_url": "http://127.0.0.1:8000/payments",
        }

        res = self.fa_client.post(f"{API_BASE_URL}/intent/", json=intent)

        assert res.status_code == 200
        res_data = res.json()
        assert res_data["amount"] == 36000
        returned_tts = [tt["id"] for tt in res_data["ticket_types"]]
        for tt in ticket_types:
            assert str(tt.id) in returned_tts

    def test_ipn_page(self) -> None:
        event = create_event_object(owner=self.partner.owner)
        ticket_types = [
            create_ticket_type_obj(event=event),
            create_ticket_type_obj(event=event),
            create_ticket_type_obj(event=event),
        ]
        person_data = person_fixture()
        ticket_type_data = [
            {"id": str(ticket_type.id), "amount": 1} for ticket_type in ticket_types
        ]
        intent = {
            "person": person_data,
            "ticket_types": ticket_type_data,
            "callback_url": "http://127.0.0.1:8000/payments",
        }

        create_res = self.fa_client.post(f"{API_BASE_URL}/intent/", json=intent)
        assert create_res.status_code == 200

        res = self.fa_client.get(f"{API_BASE_URL}/{create_res.json()['id']}/")
        assert res.status_code == 200
