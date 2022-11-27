import json
from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.utils import random_float, random_string
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
        assert res.json()["category"]["name"]

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
        name = random_string()
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ta_id = str(
            partner_fixtures.create_partner_person(partner=self.owner.partner).id
        )
        ticket_types = [
            event_fixtures.ticket_type_min_fixture(),
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

        res = self.client.put(
            f"/{API_VER}/events/events/{event.id}/",
            data={"event_date": 2},
            format="json",
        )
        assert res.status_code == 422

    def test_update_event__check_agent_update_replaces_original_list(self) -> None:
        # check that the TA is dropped if not included in updated list
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ta_1_id = str(
            partner_fixtures.create_partner_person(partner=self.owner.partner).id
        )
        ta_2_id = str(
            partner_fixtures.create_partner_person(partner=self.owner.partner).id
        )

        update_data = {"partner_person_ids": [ta_1_id]}
        res = self.client.put(
            f"/{API_VER}/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == status.HTTP_200_OK
        ta_ids = [ta["id"] for ta in res.json()["assigned_ticketing_agents"]]
        assert ta_1_id in ta_ids
        assert ta_2_id not in ta_ids

        update_data = {"partner_person_ids": [ta_2_id]}
        res = self.client.put(
            f"/{API_VER}/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == status.HTTP_200_OK
        ta_ids = [ta["id"] for ta in res.json()["assigned_ticketing_agents"]]
        assert ta_1_id not in ta_ids
        assert ta_2_id in ta_ids

    def test_update_event_ticket_types(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        tt1: TicketType = event_fixtures.create_ticket_type_obj(event=event)
        tt2: TicketType = event_fixtures.create_ticket_type_obj(event=event)
        tt3: TicketType = event_fixtures.create_ticket_type_obj(event=event)

        tt1_dict = {
            "name": tt1.name,
            "price": tt1.price + random_float(),
            "active": True,
            "amsg": random_string(),
            "amount": 1200,
        }
        tt2_dict = {
            "name": tt2.name,
            "price": tt2.price + random_float(),
            "active": True,
            "amsg": random_string(),
            "amount": 1200,
        }
        ttnew_dict = event_fixtures.ticket_type_min_fixture()
        update_data = {"ticket_types": [tt1_dict, tt2_dict, ttnew_dict]}

        res = self.client.put(
            f"/{API_VER}/events/events/{event.id}/", data=update_data, format="json"
        )
        assert res.status_code == 200
        tt3.refresh_from_db()
        assert not tt3.active
        assert len(res.json()["ticket_types"]) == 3
        tt_ids = [tt["id"] for tt in res.json()["ticket_types"]]
        assert str(tt1.id) in tt_ids
        assert str(tt2.id) in tt_ids
        assert str(tt3.id) not in tt_ids
        for tt in res.json()["ticket_types"]:
            if tt["id"] == str(tt1.id):
                assert tt["price"] == int(tt1_dict["price"])  # type: ignore
            if tt["id"] == str(tt2.id):
                assert tt["price"] == int(tt2_dict["price"])  # type: ignore

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
        assert "created_at" in str(res.getvalue())

    def test_list_events(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event2 = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()
        event2.created_at = date.today() - timedelta(days=1)
        event2.save()
        partner_person_schedule = event_fixtures.create_partner_person_schedule(
            event_id=str(event.id)
        )
        ticket_fixtures.create_ticket_obj(event=event)

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

        res = self.client.get(
            f"/{API_VER}/events/events/?partner_id={self.owner.partner_id}"
            "&ordering=-sales"
        )
        assert res.status_code == 200
        returned_sales_figures = [event["sales"] for event in res.json()["results"]]
        assert sorted(returned_sales_figures) == returned_sales_figures

    def test_export_events(self) -> None:
        event_fixtures.create_event_object(owner=self.owner.person)
        event2 = event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()
        event2.created_at = date.today() - timedelta(days=1)
        event2.save()

        res = self.client.get(f"/{API_VER}/events/export/csv/")
        assert res.status_code == 200
        fields = ["event_number", "name", "event_date", "sales"]
        returned_text = str(res.getvalue())
        for field in fields:
            assert field in returned_text

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

    def test_list_categories(self) -> None:
        event_fixtures.create_event_category_obj()

        res = self.client.get(f"/{API_VER}/events/categories/")

        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_category__filterable_by_assigned_events(self) -> None:
        category_1_id = str(event_fixtures.create_event_category_obj().id)
        category_2_id = str(event_fixtures.create_event_category_obj().id)
        category_3_id = str(event_fixtures.create_event_category_obj().id)
        event_fixtures.create_event_object(
            self.owner.person, state="AE", category_id=category_1_id
        )
        event_fixtures.create_event_object(
            self.owner.person, state="AE", category_id=category_1_id
        )
        event_fixtures.create_event_object(self.owner.person, category_id=category_3_id)

        res = self.client.get(f"/{API_VER}/events/categories/?event__isnull=false")

        assert res.status_code == 200
        returned_cat_ids = [cat["id"] for cat in res.json()]
        assert category_1_id in returned_cat_ids
        assert category_3_id in returned_cat_ids
        assert category_2_id not in returned_cat_ids

        res = self.client.get(f"/{API_VER}/events/categories/?event__isnull=True")

        assert res.status_code == 200
        returned_cat_ids = [cat["id"] for cat in res.json()]
        assert category_1_id not in returned_cat_ids
        assert category_3_id not in returned_cat_ids
        assert category_2_id in returned_cat_ids

        res = self.client.get(
            f"/{API_VER}/events/categories/?event__isnull=False&event__event_state=AE"
        )

        assert res.status_code == 200
        returned_cat_ids = [cat["id"] for cat in res.json()]
        assert category_1_id in returned_cat_ids
        assert category_3_id not in returned_cat_ids
        assert category_2_id not in returned_cat_ids
        assert len(returned_cat_ids) == 1

    def test_reminder_optin(self) -> None:
        event = event_fixtures.create_event_object()

        res = self.client.post(f"/{API_VER}/events/reminder/optin/{event.id}/")

        assert res.status_code == 200
        assert res.json()["done"]

    def test_highlighted_events(self) -> None:
        category_1_id = str(event_fixtures.create_event_category_obj().id)
        category_2_id = str(event_fixtures.create_event_category_obj().id)

        event = event_fixtures.create_event_object(
            owner=self.owner.person, category_id=category_1_id
        )
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person, 900.0)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        event_2 = event_fixtures.create_event_object(
            owner=self.owner.person, category_id=category_2_id
        )
        ticket_type_2 = event_fixtures.create_ticket_type_obj(event=event_2)
        payment = payment_fixtures.create_payment_object(self.owner.person, 500.0)
        ticket_fixtures.create_ticket_obj(ticket_type_2, payment)
        ticket_fixtures.create_ticket_obj(ticket_type_2, payment)

        res = self.client.get(f"/{API_VER}/events/highlighted/")

        assert res.status_code == 200
        assert res.json()["results"][0]["id"] == str(event.id)
        assert res.json()["results"][1]["id"] == str(event_2.id)

        res = self.client.get(
            f"/{API_VER}/events/highlighted/?category_id={category_1_id}"
        )

        assert res.status_code == 200
        returned_event_ids = [event["id"] for event in res.json()["results"]]
        assert str(event.id) in returned_event_ids
        assert str(event_2.id) not in returned_event_ids

    def test_partner_events_count(self) -> None:
        event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object(owner=self.owner.person)
        event_fixtures.create_event_object()

        res = self.client.get(
            f"/{API_VER}/events/partner/count/{self.owner.partner_id}/"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 2

    def test_events_list__filterable_by_multiple_values(self) -> None:
        category_1_id = str(event_fixtures.create_event_category_obj().id)
        category_2_id = str(event_fixtures.create_event_category_obj().id)
        assert category_1_id != category_2_id
        event_1 = event_fixtures.create_event_object(
            owner=self.owner.person, category_id=category_1_id
        )
        event_2 = event_fixtures.create_event_object(
            owner=self.owner.person, category_id=category_2_id
        )
        event_3 = event_fixtures.create_event_object(
            owner=self.owner.person, category_id=category_1_id
        )

        res = self.client.get(f"/{API_VER}/events/events/?category_id={category_1_id}")
        assert res.status_code == 200
        returned_ids = [event["id"] for event in res.json()["results"]]
        assert str(event_1.id) in returned_ids
        assert str(event_3.id) in returned_ids
        assert str(event_2.id) not in returned_ids

        res = self.client.get(
            f"/{API_VER}/events/events/?category_id__in={category_1_id},{category_2_id}"
        )
        assert res.status_code == 200
        returned_ids = [event["id"] for event in res.json()["results"]]
        assert str(event_1.id) in returned_ids
        assert str(event_3.id) in returned_ids
        assert str(event_2.id) in returned_ids

    def test_validate_promo_code(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        event_id = str(event.id)
        promo = event_fixtures.create_event_promo_obj(event)
        code = promo.name
        fake_promo = random_string()
        pre_use_limit = promo.use_limit

        res = self.client.get(f"/{API_VER}/events/validate/{event_id}/promo/{code}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(promo.id)
        # check that the promo is redeemed
        promo.refresh_from_db()
        assert promo.use_limit == pre_use_limit - 1

        res = self.client.get(
            f"{API_VER}/events/validate/{event_id}/promo/{fake_promo}/"
        )

        assert res.status_code == 404

        promo.expiry = date.today() - timedelta(days=1)
        promo.save()
        res = self.client.get(
            f"{API_VER}/events/validate/{event_id}/promo/{fake_promo}/"
        )

        assert res.status_code == 404

        promo.expiry = date.today() + timedelta(days=30)
        promo.use_limit = 0
        promo.save()
        res = self.client.get(
            f"{API_VER}/events/validate/{event_id}/promo/{fake_promo}/"
        )

        assert res.status_code == 404
