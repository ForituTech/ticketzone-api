from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from events.constants import EventState
from events.fixtures import event_fixtures
from events.models import TicketType
from partner.constants import PersonType
from partner.fixtures import partner_fixtures


class EventTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        self.ticketing_agent = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        self.auth_header = {
            "Authorization": partner_fixtures.create_auth_token(self.owner.person)
        }
        self.ta_auth_header = {
            "Authorization": partner_fixtures.create_auth_token(
                self.ticketing_agent.person
            )
        }
        self.client = APIClient(**self.auth_header)
        self.ta_client = APIClient(**self.ta_auth_header)

    def tearDown(self) -> None:
        self.owner.person.delete()

    def test_create_event__no_data(self) -> None:
        res = self.client.post("/events/events/", data={}, format="json")
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_event(self) -> None:
        res = self.client.post(
            "/events/events/", data=event_fixtures.event_fixture(), format="json"
        )
        assert res.status_code == status.HTTP_200_OK

    def test_create_event__non_owner(self) -> None:
        res = self.ta_client.post(
            "/events/events/", data=event_fixtures.event_fixture(), format="json"
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_update_event(self) -> None:
        name = "Test Event Update"
        update_data = {
            "name": name,
        }
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.client.put(
            f"/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["name"] == name

    def test_update_event__non_owner(self) -> None:
        name = "Test Event Update"
        update_data = {
            "name": name,
        }
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.ta_client.put(
            f"/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == 403

    def test_read_event(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.client.put(f"/events/events/{event.id}/", format="json")
        assert res.status_code == 200
        assert res.json()["id"] == str(event.id)

    def test_create_ticket_type(self) -> None:
        res = self.client.post(
            "/events/tickets/", data=event_fixtures.ticket_type_fixture(), format="json"
        )
        assert res.status_code == status.HTTP_200_OK

    def test_list_ticket_types__generic(self) -> None:
        res = self.client.get("/events/tickets/")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_list_ticket_types(self) -> None:
        event1 = event_fixtures.create_event_object(self.owner.person)
        event2 = event_fixtures.create_event_object(self.owner.person)
        event_fixtures.create_ticket_type_obj(event=event1)
        event_fixtures.create_ticket_type_obj(event=event2)
        res = self.client.get(f"/events/tickets/?event_id={event1.id}")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] == 1

    def test_update_ticket_type(self) -> None:
        ticket: TicketType = event_fixtures.create_ticket_type_obj(
            owner=self.owner.person
        )
        name = "Test VIP ticket"
        data = {
            "name": name,
        }
        res = self.client.put(f"/events/tickets/{ticket.id}/", data=data, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["name"] == name

    def test_event_search(self) -> None:
        event = event_fixtures.create_event_object()
        res = self.client.get(f"/events/search/{event.event_location}%20{event.name}/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_event_search__by_description(self) -> None:
        event = event_fixtures.create_event_object()
        res = self.client.get(f"/events/search/{event.description}/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_event_search__non_existant_terms(self) -> None:
        event = event_fixtures.create_event_object()
        res = self.client.get(f"/events/search/{event.event_location}-1234/")

        assert res.status_code == 200
        assert res.json()["count"] == 0

    def test_event_filter(self) -> None:
        event = event_fixtures.create_event_object()
        res = self.client.get(f"/events/events/?event_date={event.event_date}")

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/events/events/?partner={event.partner.id}")

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/events/events/?event_state={event.event_state}")

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/events/events/?event_state={EventState.CLOSED}")

        assert res.status_code == 200
        assert res.json()["count"] == 0

        event.delete()
