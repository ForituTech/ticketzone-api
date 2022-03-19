from datetime import date, timedelta
from typing import Any
from unittest import mock

from django.test import TestCase
from rest_framework.test import APIClient

from eticketing_api import settings
from events.fixtures import event_fixtures
from events.models import Person, Ticket
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from partner.tasks import send_out_promos, send_out_reminders
from partner.utils import verify_password
from payments.fixtures import payment_fixtures
from tickets.fixtures import ticket_fixtures


class PartnerTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        self.ticketing_agent = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        auth_header = {
            "Authorization": partner_fixtures.create_auth_token(self.owner.person)
        }
        ta_auth_header = {
            "Authorization": partner_fixtures.create_auth_token(
                self.ticketing_agent.person
            )
        }
        self.authed_client = APIClient(False, **auth_header)
        self.ta_client = APIClient(False, **ta_auth_header)
        self.unauthed_client = APIClient(
            False,
        )

    def test_login__authed(self) -> None:
        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": "123456",
        }
        res = self.authed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 202

    def test_login(self) -> None:
        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": "123456",
        }
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

        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": "123457",
        }
        res = self.unauthed_client.post(
            "/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]

    def test_read_partner(self) -> None:
        res = self.authed_client.get(
            f"/partner/partner/{self.owner.partner.id}/",
        )
        assert res.status_code == 200
        assert self.owner.partner.name == res.json()["name"]

    def test_read_partner__unrelated(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        res = self.authed_client.get(
            f"/partner/partner/{partner.id}/",
        )
        assert res.status_code == 403

    def test_update_partner(self) -> None:
        code = 789101112
        update_data = {"banking_info": {"bank_code": code}}
        res = self.authed_client.put(
            f"/partner/partner/{self.owner.partner.id}/",
            data=update_data,
            format="json",
        )
        assert res.status_code == 200
        assert self.owner.partner.name == res.json()["name"]
        assert self.owner.partner.banking_info.bank_code == code

    def test_update_partner__unrelated(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        update_data = {"banking_info": {"bank_code": 789101112}}
        res = self.authed_client.put(
            f"/partner/partner/{partner.id}/",
            data=update_data,
            format="json",
        )
        assert res.status_code == 403
        assert "detail" in res.json()
        assert "ACCESS_ONLY_FOR_SELF" in res.json()["detail"]

    def test_person_read(self) -> None:
        res = self.authed_client.get(
            f"/partner/person/{self.owner.person.id}/",
        )
        assert res.status_code == 200
        assert self.owner.person.phone_number == res.json()["phone_number"]

    def test_person_read__unrelated(self) -> None:
        person = partner_fixtures.create_person_obj()
        res = self.authed_client.get(
            f"/partner/person/{person.id}/",
        )
        assert res.status_code == 403
        assert "detail" in res.json()
        assert "ACCESS_ONLY_FOR_SELF" in res.json()["detail"]

    def test_person_create(self) -> None:
        person_data = partner_fixtures.person_fixture()
        person_data["hashed_password"] = "1234"
        res = self.unauthed_client.post(
            "/partner/person/", data=person_data, format="json"
        )
        assert res.status_code == 200
        new_person = res.json()
        assert new_person
        for key in person_data.keys():
            if key != "hashed_password":
                assert new_person[key] == person_data[key]
            else:
                assert verify_password("1234", new_person[key])
        assert "Authorization" in res.headers

    def test_partner_person_create(self) -> None:
        partner_person_data = partner_fixtures.partner_person_fixture()
        partner_person_data["person"] = partner_fixtures.person_fixture()
        partner_person_data["partner_id"] = str(partner_person_data["partner_id"])

        res = self.authed_client.post(
            "/partner/partnership/person/", data=partner_person_data, format="json"
        )

        assert res.status_code == 200
        assert "person_id" in res.json()

    def test_partner_person_create__non_owner(self) -> None:
        partner_person_data = partner_fixtures.partner_person_fixture()
        partner_person_data["person"] = partner_fixtures.person_fixture()
        partner_person_data["partner_id"] = str(partner_person_data["partner_id"])

        res = self.ta_client.post(
            "/partner/partnership/person/", data=partner_person_data, format="json"
        )

        assert res.status_code == 403

    def test_partner_person_create__invalid_number(self) -> None:
        partner_person_data = partner_fixtures.partner_person_fixture()
        partner_person_data["person"] = partner_fixtures.person_fixture()
        partner_person_data["partner_id"] = str(partner_person_data["partner_id"])
        partner_person_data["person"]["phone_number"] = partner_person_data["person"][
            "phone_number"
        ].strip("+")

        res = self.authed_client.post(
            "/partner/partnership/person/", data=partner_person_data, format="json"
        )

        assert res.status_code == 422

    def test_partner_person_update(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        update_data = {
            "person_type": PersonType.PARTNER_MEMBER,
        }

        res = self.authed_client.put(
            f"/partner/partnership/person/{partner_person.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 200
        assert res.json()["person_type"] == PersonType.PARTNER_MEMBER.value

    def test_partner_person_update__non_owner(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        update_data = {
            "person_type": PersonType.PARTNER_MEMBER,
        }

        res = self.ta_client.put(
            f"/partner/partnership/person/{partner_person.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_partner_person_read(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.authed_client.get(
            f"/partner/partnership/person/{partner_person.id}/",
        )

        assert res.status_code == 200
        read_data = res.json()
        assert read_data["person_id"] == str(partner_person.person.id)
        assert read_data["partner_id"] == str(partner_person.partner.id)

    def test_partner_person_read__non_owner(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.ta_client.get(
            f"/partner/partnership/person/{partner_person.id}/",
        )

        assert res.status_code == 403

    def test_deactivated_user_raises_access_denied(self) -> None:
        self.owner.is_active = False
        self.owner.save()

        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.authed_client.get(
            f"/partner/partnership/person/{partner_person.id}/",
        )

        self.owner.is_active = True
        self.owner.save()

        assert res.status_code == 403

    def test_partner_sales(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.authed_client.get("/partner/sales/")

        assert res.status_code == 200
        assert "sales" in res.json()

    def test_partner_redemtion_rate(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.redeemed = True
        ticket.save()
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.authed_client.get("/partner/events/redemtion-rate/")

        assert res.status_code == 200
        assert "rate" in res.json()

    def test_partner_events_ranked(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        event_fixtures.create_event_object(owner=self.owner.person)

        res = self.authed_client.get("/partner/events/ranked/")

        assert res.status_code == 200
        assert res.json()[0]["id"] == str(event.id)

    def test_list_ticket_types_with_sales(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.authed_client.get(f"/partner/events/tickets/{event.id}/")

        assert res.status_code == 200
        assert "sales" in res.json()[0]

    def test_partner_promo_optin(self) -> None:
        partner = partner_fixtures.create_partner_obj()

        res = self.authed_client.post(f"/partner/promo/optin/{partner.id}/")

        assert res.status_code == 200
        assert res.json()["done"]

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_reminders(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        event = event_fixtures.create_event_object(owner=partner.owner)
        person: Person = partner_fixtures.create_person_obj()
        ticket: Ticket = ticket_fixtures.create_ticket_obj(event=event, person=person)
        ticket_fixtures.create_ticket_obj(event=event, payment=ticket.payment)
        partner_fixtures.create_reminder_optin_object(
            person=person, event=ticket.ticket_type.event
        )

        send_out_reminders()

        mock_send_sms.assert_called_once_with(
            args=(
                ticket.payment.person_id,
                settings.REMINDER_SMS.format(
                    ticket.payment.person.name, ticket.ticket_type.event.name
                ),
            ),
            queue="main_queue",
        )

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_reminders__no_optin(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        event = event_fixtures.create_event_object(owner=partner.owner)
        ticket_fixtures.create_ticket_obj(event=event)

        send_out_reminders()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_reminders__no_sms_package(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        event = event_fixtures.create_event_object(owner=partner.owner)
        ticket: Ticket = ticket_fixtures.create_ticket_obj(event=event)
        partner_fixtures.create_reminder_optin_object(event=ticket.ticket_type.event)

        send_out_reminders()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_reminders__no_verified_sms_package(
        self, mock_send_sms: Any
    ) -> None:
        partner = partner_fixtures.create_partner_obj()
        sms_package = partner_fixtures.create_partner_sms_obj(partner=partner)
        sms_package.verified = False
        sms_package.save()
        event = event_fixtures.create_event_object(owner=partner.owner)
        ticket: Ticket = ticket_fixtures.create_ticket_obj(event=event)
        partner_fixtures.create_reminder_optin_object(event=ticket.ticket_type.event)

        send_out_reminders()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        promo = partner_fixtures.create_partner_promo_obj(partner=partner)
        promo.last_run = date.today() - timedelta(weeks=2)
        promo.save()
        optin = partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        mock_send_sms.assert_called_once_with(
            args=(optin.person.id, promo.message),
            queue="main_queue",
        )

        promo.refresh_from_db()

        assert promo.last_run == date.today()

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos__no_sms_package(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_promo_obj(partner=partner)
        partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos__no_optin(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        partner_fixtures.create_partner_promo_obj(partner=partner)

        send_out_promos()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos__no_verified_sms_package(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        sms_package = partner_fixtures.create_partner_sms_obj(partner=partner)
        sms_package.verified = False
        sms_package.save()
        partner_fixtures.create_partner_promo_obj(partner=partner)
        partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        assert not mock_send_sms.called

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos__no_running_promos(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        promo = partner_fixtures.create_partner_promo_obj(partner=partner)
        promo.starts_on = date.today() + timedelta(weeks=12)
        promo.save()
        partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        assert not mock_send_sms.called
