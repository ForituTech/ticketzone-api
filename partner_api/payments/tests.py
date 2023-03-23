from unittest import mock
from unittest.mock import Mock

from django.test import TransactionTestCase
from fastapi.testclient import TestClient

from eticketing_api import settings
from eticketing_api.asgi import app
from events.fixtures.event_fixtures import create_event_object, create_ticket_type_obj
from partner.fixtures.partner_fixtures import create_partner_obj, person_fixture
from partner_api.auth.tests.fixtures import create_partner_api_credentials_obj
from partner_api.auth.utils import create_auth_token
from payments.constants import PaymentProviders
from payments.intergrations.ipay import iPayMPesa

API_BASE_URL = "/v1/payments"


class PaymentTestCase(TransactionTestCase):
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
        returned_tts = [(tt["id"], tt["amount"]) for tt in res_data["ticket_types"]]
        for tt in ticket_type_data:
            assert (tt["id"], tt["amount"]) in returned_tts

    @mock.patch.object(iPayMPesa, "c2b_receive")
    def test_create_payment__from_intent(self, mock_c2b_recieve: Mock) -> None:
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

        intent_res = self.fa_client.post(f"{API_BASE_URL}/intent/", json=intent)
        assert intent_res.status_code == 200
        intent = intent_res.json()

        payment_data = {
            "intent_id": intent["id"],
            "made_through": PaymentProviders.MPESA.value,
        }

        res = self.fa_client.post(f"{API_BASE_URL}/", json=payment_data)
        assert res.status_code == 200
        mock_c2b_recieve.assert_called()

    @mock.patch.object(iPayMPesa, "c2b_receive")
    def test_create_payment__from_intent__with_new_person_details(
        self, mock_c2b_recieve: Mock
    ) -> None:
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

        intent_res = self.fa_client.post(f"{API_BASE_URL}/intent/", json=intent)
        assert intent_res.status_code == 200
        intent = intent_res.json()

        new_person_data = person_fixture()
        payment_data = {
            "intent_id": intent["id"],
            "made_through": PaymentProviders.MPESA.value,
            "person": new_person_data,
        }

        res = self.fa_client.post(f"{API_BASE_URL}/", json=payment_data)
        assert res.status_code == 200
        assert res.json()["person"]["phone_number"] == new_person_data["phone_number"]
        mock_c2b_recieve.assert_called()

    def test_read_intent(self) -> None:
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

        intent_res = self.fa_client.post(f"{API_BASE_URL}/intent/", json=intent)
        assert intent_res.status_code == 200
        intent = intent_res.json()

        res = self.fa_client.get(f"{API_BASE_URL}/intent/{intent['id']}/")
        assert res.status_code == 200
