import json
from datetime import date, timedelta
from random import randint
from typing import Any, Dict

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from eticketing_api import settings
from events.constants import EventState
from events.fixtures import event_fixtures
from events.models import TicketType
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from payments.fixtures import payment_fixtures
from tickets.fixtures import ticket_fixtures

API_VER = settings.API_VERSION_STRING


class EventTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        self.ticketing_agent = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        self.auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_auth_token(self.owner.person)
        }
        self.ta_auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_auth_token(
                self.ticketing_agent.person
            )
        }
        self.client = APIClient(False, **self.auth_header)
        self.ta_client = APIClient(False, **self.ta_auth_header)

    def test_create_event__no_data(self) -> None:
        res = self.client.post(f"/{API_VER}/events/events/", data={})
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_event(self) -> None:
        data = event_fixtures.event_fixture(partner_id=str(self.owner.partner.id))
        ta_id = str(
            partner_fixtures.create_partner_person(partner=self.owner.partner).id
        )
        data["partner_person_ids"] = json.dumps([ta_id])
        ticket_types = [
            event_fixtures.ticket_type_min_fixture(),
            event_fixtures.ticket_type_min_fixture(),
        ]
        data["ticket_types"] = json.dumps(ticket_types)
        ticket_type_names = [tt["name"] for tt in ticket_types]

        event_promos = [
            event_fixtures.event_promo_min_fixture(),
            event_fixtures.event_promo_min_fixture(),
        ]
        data["event_promotions"] = json.dumps(event_promos)

        res = self.client.post(f"/{API_VER}/events/events/", data=data)
        assert res.status_code == status.HTTP_200_OK
        ta_ids = [ta["id"] for ta in res.json()["assigned_ticketing_agents"]]
        assert ta_id in ta_ids
        tt_names = [tt["name"] for tt in res.json()["ticket_types"]]
        for tt_name in tt_names:
            assert tt_name in ticket_type_names

        promo_res = self.client.get(
            f"/{API_VER}/events/event/promo/?event_id={res.json()['id']}"
        )

        assert promo_res.status_code == 200
        assert promo_res.json()["count"] == 2

    def test_create_event__non_owner(self) -> None:
        res = self.ta_client.post(
            f"/{API_VER}/events/events/",
            data=event_fixtures.event_fixture(),
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_update_event(self) -> None:
        name = "Test Event Update"
        ta_id = str(
            partner_fixtures.create_partner_person(partner=self.owner.partner).id
        )
        ticket_types = [
            event_fixtures.ticket_type_min_fixture(),
            event_fixtures.ticket_type_min_fixture(),
        ]
        ticket_type_names = [tt["name"] for tt in ticket_types]

        event_promos = [
            event_fixtures.event_promo_min_fixture(),
            event_fixtures.event_promo_min_fixture(),
        ]
        update_data = {
            "name": name,
            "partner_person_ids": [ta_id],
            "ticket_types": ticket_types,
            "event_promotions": event_promos,
        }
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.client.put(
            f"/{API_VER}/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["name"] == name
        ta_ids = [ta["id"] for ta in res.json()["assigned_ticketing_agents"]]
        assert ta_id in ta_ids
        tt_names = [tt["name"] for tt in res.json()["ticket_types"]]
        for tt_name in tt_names:
            assert tt_name in ticket_type_names

        promo_res = self.client.get(
            f"/{API_VER}/events/event/promo/?event_id={res.json()['id']}"
        )

        assert promo_res.status_code == 200
        assert promo_res.json()["count"] == 2

    def test_update_event__non_owner(self) -> None:
        name = "Test Event Update"
        update_data = {
            "name": name,
        }
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.ta_client.put(
            f"/{API_VER}/events/events/{event.id}/", data=update_data
        )
        assert res.status_code == 403

    def test_read_event(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket = ticket_fixtures.create_ticket_obj(event=event)
        ticket2 = ticket_fixtures.create_ticket_obj(event=event)
        ticket3 = ticket_fixtures.create_ticket_obj(event=event)
        ticket2.redeemed = True
        ticket2.save()
        ticket3.redeemed = True
        ticket3.save()
        sales = ticket.payment.amount + ticket2.payment.amount + ticket3.payment.amount

        res = self.client.get(f"/{API_VER}/events/events/{event.id}/")
        assert res.status_code == 200
        assert res.json()["id"] == str(event.id)
        assert res.json()["tickets_sold"] == 3
        assert int(res.json()["redemption_rate"]) == 66
        assert res.json()["sales"] == sales

    def test_list_events(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event2 = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()
        event2.created_at = date.today() - timedelta(days=1)
        event2.save()
        partner_person_schedule = event_fixtures.create_partner_person_schedule(
            event_id=str(event.id)
        )

        res = self.client.get(
            f"/{API_VER}/events/events/?partner_id={self.owner.partner_id}"
            "&ordering=-created_at,updated_at"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 2
        returned_events_created_at = [
            event["created_at"] for event in res.json()["results"]
        ]
        assert returned_events_created_at[0] > returned_events_created_at[1]

        for event_dict in res.json()["results"]:
            if event_dict["id"] == event.id:
                assert (
                    event_dict["assigned_ticketing_agents"]["id"]
                    == partner_person_schedule.id
                )
            assert "event_state" in event_dict

    def test_export_events(self) -> None:
        event_fixtures.create_event_object(owner=self.owner.person)
        event2 = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()
        event2.created_at = date.today() - timedelta(days=1)
        event2.save()

        res = self.client.get(f"/{API_VER}/events/export/csv/")
        assert res.status_code == 200

    def test_create_ticket_type(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        data = event_fixtures.ticket_type_fixture(event_id=str(event.id))
        res = self.client.post(f"/{API_VER}/events/tickets/", data=data, format="json")
        assert res.status_code == status.HTTP_200_OK

    def test_list_ticket_types__generic(self) -> None:
        res = self.client.get(f"/{API_VER}/events/tickets/")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_list_ticket_types(self) -> None:
        event1 = event_fixtures.create_event_object(self.owner.person)
        event2 = event_fixtures.create_event_object(self.owner.person)
        event_fixtures.create_ticket_type_obj(event=event1)
        event_fixtures.create_ticket_type_obj(event=event2)
        res = self.client.get(f"/{API_VER}/events/tickets/?event_id={event1.id}")
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
        res = self.client.put(
            f"/{API_VER}/events/tickets/{ticket.id}/", data=data, format="json"
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["name"] == name

    def test_event_search(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()
        res = self.client.get(
            f"/{API_VER}/events/events/?search={event.event_location}%20{event.name}/"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/{API_VER}/events/events/?search={event.description}/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_event_search__non_existant_terms(self) -> None:
        event = event_fixtures.create_event_object()
        res = self.client.get(
            f"/{API_VER}/events/events/?search={event.event_location}-1234/"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 0

    def test_event_filter_by_category(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        category = event_fixtures.create_event_category_obj()
        event.category = category
        event.save()
        res = self.client.get(f"/{API_VER}/events/events/?category={category.id}")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_event_filter(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        res = self.client.get(
            f"/{API_VER}/events/events/?event_date={event.event_date}"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/{API_VER}/events/events/?partner={event.partner.id}")

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(
            f"/{API_VER}/events/events/?event_state={event.event_state}"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(
            f"/{API_VER}/events/events/?event_state={EventState.CLOSED}"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 0

        event.delete()

    def test_event_promo_create(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event_data = event_fixtures.event_promo_fixture(event_id=str(event.id))
        res = self.client.post(
            f"/{API_VER}/events/event/promo/", data=event_data, format="json"
        )

        assert res.status_code == 200
        assert res.json()["event_id"] == str(event.id)

    def test_event_promo_create__non_self(self) -> None:
        event_data = event_fixtures.event_promo_fixture()
        res = self.client.post(
            f"/{API_VER}/events/event/promo/", data=event_data, format="json"
        )

        assert res.status_code == 403

    def test_event_promo_create__non_owner(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event_data = event_fixtures.event_promo_fixture(event_id=str(event.id))
        res = self.ta_client.post(
            f"/{API_VER}/events/event/promo/", data=event_data, format="json"
        )

        assert res.status_code == 403

    def test_list_event_promos(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_promo_obj(event=event)
        event_fixtures.create_event_promo_obj()

        res = self.client.get(f"/{API_VER}/events/event/promo/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_update_event_promo(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        promo = event_fixtures.create_event_promo_obj(event=event)
        rate = 15
        update_data = {"promotion_rate": rate}

        res = self.client.put(
            f"/{API_VER}/events/event/promo/{promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 200
        assert res.json()["promotion_rate"] == rate

    def test_update_event_promo__non_self(self) -> None:
        promo = event_fixtures.create_event_promo_obj()
        rate = 15
        update_data = {"promotion_rate": rate}

        res = self.client.put(
            f"/{API_VER}/events/event/promo/{promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_update_event_promo__non_owner(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        promo = event_fixtures.create_event_promo_obj(event=event)
        rate = 15
        update_data = {"promotion_rate": rate}

        res = self.ta_client.put(
            f"/{API_VER}/events/event/promo/{promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_ticket_promo_create(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_promo_data = event_fixtures.ticket_promo_fixture(str(ticket_type.id))

        res = self.client.post(
            f"/{API_VER}/events/ticket/promo/", data=ticket_promo_data, format="json"
        )

        assert res.status_code == 200
        assert res.json()["ticket_id"] == str(ticket_type.id)

    def test_ticket_promo_create__non_self(self) -> None:
        ticket_promo_data = event_fixtures.ticket_promo_fixture()

        res = self.client.post(
            f"/{API_VER}/events/ticket/promo/", data=ticket_promo_data, format="json"
        )

        assert res.status_code == 403

    def test_ticket_promo_create__non_owner(self) -> None:
        ticket_promo_data = event_fixtures.ticket_promo_fixture()

        res = self.ta_client.post(
            f"/{API_VER}/events/ticket/promo/", data=ticket_promo_data, format="json"
        )

        assert res.status_code == 403

    def test_ticket_promo_list(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        event_fixtures.create_ticket_promo_obj(ticket_type)
        event_fixtures.create_ticket_promo_obj()

        res = self.client.get(f"/{API_VER}/events/ticket/promo/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_ticket_promo_update(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_promo = event_fixtures.create_ticket_promo_obj(ticket_type)
        rate = randint(11, 30)

        update_data = {
            "promotion_rate": rate,
        }

        res = self.client.put(
            f"/{API_VER}/events/ticket/promo/{ticket_promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 200
        assert res.json()["promotion_rate"] == rate

    def test_ticket_promo_update__non_self(self) -> None:
        ticket_promo = event_fixtures.create_ticket_promo_obj()
        rate = randint(11, 30)

        update_data = {
            "promotion_rate": rate,
        }

        res = self.client.put(
            f"/{API_VER}/events/ticket/promo/{ticket_promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_ticket_promo_update__non_owner(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_promo = event_fixtures.create_ticket_promo_obj(ticket_type)
        rate = randint(11, 30)

        update_data = {
            "promotion_rate": rate,
        }

        res = self.ta_client.put(
            f"/{API_VER}/events/ticket/promo/{ticket_promo.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_code_redemption(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_promo = event_fixtures.create_ticket_promo_obj(ticket_type)

        data = {
            "target_ids": [str(ticket_type.id)],
        }

        res = self.client.post(
            f"/{API_VER}/events/redeem/code/{ticket_promo.name}/",
            data=data,
            format="json",
        )

        assert res.status_code == 200
        assert eval(res.json())[0]["rate"] == ticket_promo.promotion_rate

    def test_code_redemption__no_pre_targeting(self) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_promo = event_fixtures.create_ticket_promo_obj(ticket_type)
        pre_use_limit_value = ticket_promo.use_limit

        data: Dict[str, Any] = {
            "target_ids": [],
        }

        res = self.client.post(
            f"/{API_VER}/events/redeem/code/{ticket_promo.name}/",
            data=data,
            format="json",
        )

        assert res.status_code == 200
        ticket_promo.refresh_from_db()
        assert ticket_promo.use_limit == pre_use_limit_value
        assert not eval(res.json())

    def test_list_categories(self) -> None:
        event_fixtures.create_event_category_obj()

        res = self.client.get(f"/{API_VER}/events/categories/")

        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_reminder_optin(self) -> None:
        event = event_fixtures.create_event_object()

        res = self.client.post(f"/{API_VER}/events/reminder/optin/{event.id}/")

        assert res.status_code == 200
        assert res.json()["done"]

    def test_highlighted_events(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        event_fixtures.create_event_object(owner=self.owner.person)

        res = self.client.get(f"/{API_VER}/events/highlighted/")

        assert res.status_code == 200
        assert res.json()["results"][0]["id"] == str(event.id)

    def test_partner_events_count(self) -> None:
        event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()

        res = self.client.get(
            f"/{API_VER}/events/partner/count/{self.owner.partner_id}/"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 2
