from django.test import TransactionTestCase
from fastapi.testclient import TestClient

from eticketing_api import settings
from eticketing_api.asgi import app
from events.fixtures.event_fixtures import create_event_object
from partner.fixtures.partner_fixtures import create_partner_obj
from partner_api.auth.tests.fixtures import create_partner_api_credentials_obj
from partner_api.auth.utils import create_auth_token

API_BASE_URL = "/v1/events"


class AuthTestCase(TransactionTestCase):
    def setUp(self) -> None:
        # fastapi client
        self.partner = create_partner_obj()
        self.api_credentials = create_partner_api_credentials_obj(self.partner)
        self.token = create_auth_token(api_creds=self.api_credentials)
        self.fa_client = TestClient(
            app, headers={settings.EXTERNAL_API_AUTH_HEADER: self.token["access_token"]}
        )

    def test_list_events(self) -> None:
        events = [
            create_event_object(owner=self.partner.owner),
            create_event_object(owner=self.partner.owner),
            create_event_object(),
        ]

        res = self.fa_client.get(f"{API_BASE_URL}/")
        assert res.status_code == 200
        returned_data = res.json()
        assert returned_data["total"] == 2
        returned_ids = [item["id"] for item in returned_data["items"]]
        assert str(events[0].id) in returned_ids
        assert str(events[1].id) in returned_ids
        assert str(events[2].id) not in returned_ids

    def test_read_event(self) -> None:
        event = create_event_object(owner=self.partner.owner)

        res = self.fa_client.get(f"{API_BASE_URL}/{event.id}/")
        assert res.status_code == 200
        assert res.json()["id"] == str(event.id)

    def test_read_event__unrelated(self) -> None:
        event = create_event_object()

        res = self.fa_client.get(f"{API_BASE_URL}/{event.id}/")
        assert res.status_code == 404
