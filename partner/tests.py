from datetime import date, timedelta
from typing import Any, Optional
from unittest import mock

from django.test import Client, TestCase
from rest_framework.test import APIClient

from core.utils import random_string
from eticketing_api import settings
from events.fixtures import event_fixtures
from events.models import Person, Ticket
from owners.fixtures import owner_fixtures
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from partner.models import Partner, PartnerPerson, PartnerSMS
from partner.services import partner_service, person_service
from partner.tasks import reconcile_payments, send_out_promos, send_out_reminders
from partner.utils import random_password, verify_otp, verify_password
from payments.fixtures import payment_fixtures
from tickets.fixtures import ticket_fixtures

API_VER = settings.API_VERSION_STRING


class PartnerTestCase(TestCase):
    @mock.patch("partner.fixtures.partner_fixtures.random_password")
    def setUp(self, mock_random_password: Any) -> None:
        self.password = random_password()
        mock_random_password.return_value = self.password
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        self.ticketing_agent = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_auth_token(self.owner.person)
        }
        ta_auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_auth_token(
                self.ticketing_agent.person
            )
        }
        self.authed_client: Client = APIClient(False, **auth_header)
        self.ta_client: Client = APIClient(False, **ta_auth_header)
        self.unauthed_client: Client = APIClient(False)

    def test_login__authed(self) -> None:
        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": self.password,
        }
        res = self.authed_client.post(
            f"/{API_VER}/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 200

    def test_login(self) -> None:
        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": self.password,
        }
        res = self.unauthed_client.post(
            f"/{API_VER}/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 200
        assert "token" in res.json()

    def test_login__no_credentials(self) -> None:
        login_credentials = {
            "phone_number": partner_fixtures.random_phone_number(),
            "password": "123456",
        }
        res = self.unauthed_client.post(
            f"/{API_VER}/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]

        login_credentials = {
            "phone_number": str(self.owner.person.phone_number),
            "password": "123457",
        }
        res = self.unauthed_client.post(
            f"/{API_VER}/partner/login/", data=login_credentials, format="json"
        )
        assert res.status_code == 404
        assert "INVALID_CREDENTIALS" in res.json()["detail"]

    def test_read_partner(self) -> None:
        sms_package = partner_fixtures.create_partner_sms_obj(
            partner=self.owner.partner
        )
        res = self.authed_client.get(
            f"/{API_VER}/partner/partner/{self.owner.partner.id}/",
        )
        assert res.status_code == 200
        assert self.owner.partner.name == res.json()["name"]
        assert res.json()["sms_package"]["id"] == str(sms_package.id)
        assert res.json()["owner"]

    def test_read_partner__unrelated(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        res = self.authed_client.get(
            f"/{API_VER}/partner/partner/{partner.id}/",
        )
        assert res.status_code == 403

    def test_update_partner(self) -> None:
        code = "789101112"
        update_data = {"bank_code": code}
        res = self.authed_client.put(
            f"/{API_VER}/partner/partner/{self.owner.partner.id}/",
            data=update_data,
            format="json",
        )
        self.owner.partner.refresh_from_db()
        assert res.status_code == 200
        assert self.owner.partner.name == res.json()["name"]
        assert self.owner.partner.bank_code == code

    def test_update_partner__unrelated(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        update_data = {"banking_info": {"bank_code": "789101112"}}
        res = self.authed_client.put(
            f"/{API_VER}/partner/partner/{partner.id}/",
            data=update_data,
            format="json",
        )
        assert res.status_code == 403
        assert "detail" in res.json()
        assert "ACCESS_ONLY_FOR_SELF" in res.json()["detail"]

    def test_person_read(self) -> None:
        res = self.authed_client.get(
            f"/{API_VER}/partner/person/{self.owner.person.id}/",
        )
        assert res.status_code == 200
        assert self.owner.person.phone_number == res.json()["phone_number"]

    def test_person_read__unrelated(self) -> None:
        person = partner_fixtures.create_person_obj()
        res = self.authed_client.get(
            f"/{API_VER}/partner/person/{person.id}/",
        )
        assert res.status_code == 403
        assert "detail" in res.json()
        assert "ACCESS_ONLY_FOR_SELF" in res.json()["detail"]

    def test_person_create(self) -> None:
        person_data = partner_fixtures.person_fixture()
        person_data["hashed_password"] = "1234"
        res = self.unauthed_client.post(
            f"/{API_VER}/partner/person/", data=person_data, format="json"
        )
        assert res.status_code == 200
        new_person = res.json()
        assert new_person
        for key in person_data.keys():
            if key != "hashed_password":
                assert new_person[key] == person_data[key]
        assert settings.AUTH_HEADER in res.headers

    def test_partner_person_create(self) -> None:
        partner_person_data = partner_fixtures.partner_person_fixture()
        partner_person_data["partner_id"] = str(partner_person_data["partner_id"])

        res = self.authed_client.post(
            f"/{API_VER}/partner/partnership/person/",
            data=partner_person_data,
            format="json",
        )

        assert res.status_code == 200
        assert "person" in res.json()

    def test_partner_person_create__non_owner(self) -> None:
        partner_person_data = partner_fixtures.partner_person_fixture()
        partner_person_data["person"] = partner_fixtures.person_fixture()
        partner_person_data["partner_id"] = str(partner_person_data["partner_id"])

        res = self.ta_client.post(
            f"/{API_VER}/partner/partnership/person/",
            data=partner_person_data,
            format="json",
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
            f"/{API_VER}/partner/partnership/person/",
            data=partner_person_data,
            format="json",
        )

        assert res.status_code == 422

    def test_partner_person_update(self) -> None:
        partner_person = partner_fixtures.create_partner_person()
        update_data = {"person": partner_fixtures.person_fixture_no_password()}

        res = self.authed_client.put(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 200
        assert res.json()["person"]["name"] == update_data["person"]["name"]

    def test_partner_person_update__non_owner(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )
        update_data = {
            "person_type": PersonType.PARTNER_MEMBER,
        }

        res = self.ta_client.put(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 403

    def test_partner_person_read(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.authed_client.get(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
        )

        assert res.status_code == 200
        read_data = res.json()
        assert read_data["person"]["id"] == str(partner_person.person.id)
        assert read_data["partner_id"] == str(partner_person.partner.id)
        assert not read_data["is_scheduled"]
        assert read_data["state"] == "active"

    def test_partner_person_list(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT, partner=self.owner.partner
        )
        partner_person2 = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT, partner=self.owner.partner
        )
        partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT, partner=self.owner.partner
        )
        event = event_fixtures.create_event_object(self.owner.person)
        event_fixtures.create_partner_person_schedule(
            event_id=str(event.id), partner_person_id=str(partner_person.id)
        )
        event_fixtures.create_partner_person_schedule(
            event_id=str(event.id), partner_person_id=str(partner_person.id)
        )

        res = self.authed_client.get(
            f"/{API_VER}/partner/partnership/person/?search="
            f"{partner_person.person.email}"
        )

        assert res.status_code == 200
        read_data = res.json()
        read_person_ids = [person["id"] for person in read_data["results"]]
        assert str(partner_person.id) in read_person_ids
        assert str(partner_person2.id) not in read_person_ids

        res = self.authed_client.get(
            f"/{API_VER}/partner/partnership/person/?" "ordering=-state&person_type=TA"
        )

        assert res.status_code == 200
        read_data = res.json()
        # We need to be sure the returned data is ordered
        # by state, which means, repeated states on persons
        # need to follow each other, eg:
        # active, active, scheduled
        # a fail state would look something like:
        # scheduled, active scheduled
        returned_states = [person["state"] for person in read_data["results"]]
        assert sorted(returned_states) == returned_states

    def test_partner_person_read__non_owner(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.ta_client.get(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
        )

        assert res.status_code == 403

    def test_partner_person_delete(self) -> None:
        partner_person = partner_fixtures.create_partner_person(
            partner=self.owner.partner, person_type=PersonType.TICKETING_AGENT
        )

        res = self.authed_client.delete(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
        )
        assert res.status_code == 200
        with self.assertRaises(PartnerPerson.DoesNotExist):
            PartnerPerson.objects.get(id=partner_person.id)

    def test_deactivated_user_raises_access_denied(self) -> None:
        self.owner.is_active = False
        self.owner.save()

        partner_person = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT
        )

        res = self.authed_client.get(
            f"/{API_VER}/partner/partnership/person/{partner_person.id}/",
        )

        self.owner.is_active = True
        self.owner.save()

        assert res.status_code == 403

    def test_partner_sales(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.authed_client.get(f"/{API_VER}/partner/sales/")

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

        res = self.authed_client.get(f"/{API_VER}/partner/events/redemtion-rate/")

        assert res.status_code == 200
        assert "rate" in res.json()
        assert res.json()["rate"] == 0.5

        partner = partner_fixtures.create_partner_obj()
        event2 = event_fixtures.create_event_object(owner=partner.owner)
        ticket_type2 = event_fixtures.create_ticket_type_obj(event=event2)
        payment2 = payment_fixtures.create_payment_object(partner.owner)
        ticket_fixtures.create_ticket_obj(ticket_type2, payment2)

        res = self.unauthed_client.get(
            f"/{API_VER}/partner/events/redemtion-rate/",
            HTTP_AUTHORIZATION=partner_fixtures.get_partner_owner_auth(partner),
        )

        assert res.status_code == 200
        assert "rate" in res.json()
        assert res.json()["rate"] == 0

    def test_partner_events_ranked(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        event_fixtures.create_event_object(owner=self.owner.person)

        res = self.authed_client.get(f"/{API_VER}/partner/events/ranked/")

        assert res.status_code == 200
        assert res.json()[0]["id"] == str(event.id)

    def test_list_ticket_types_with_sales(self) -> None:
        event = event_fixtures.create_event_object(owner=self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.owner.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.authed_client.get(f"/{API_VER}/partner/events/tickets/{event.id}/")

        assert res.status_code == 200
        assert "sales" in res.json()[0]

    def test_partner_promo_optin(self) -> None:
        partner = partner_fixtures.create_partner_obj()

        res = self.authed_client.post(f"/{API_VER}/partner/promo/optin/{partner.id}/")

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
            queue=mock.ANY,
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
        sms = partner_fixtures.create_partner_sms_obj(partner=partner)
        promo = partner_fixtures.create_partner_promo_obj(partner=partner)
        promo.last_run = date.today() - timedelta(weeks=2)
        promo.save()
        optin = partner_fixtures.create_partner_promo_optin_obj(partner=partner)
        sms_pre_use = sms.sms_limit - sms.sms_used

        send_out_promos()

        mock_send_sms.assert_called_once_with(
            args=(optin.person.id, promo.message),
            queue=mock.ANY,
        )

        promo.refresh_from_db()
        sms.refresh_from_db()

        assert promo.last_run == date.today()
        assert sms_pre_use == ((sms.sms_limit - sms.sms_used) + 1)

    def send_out_promo_util(self, partner: Optional[Partner] = None) -> float:
        partner = partner if partner else partner_fixtures.create_partner_obj()
        try:
            sms = PartnerSMS.objects.get(partner_id=str(partner.id))
        except PartnerSMS.DoesNotExist:
            sms = partner_fixtures.create_partner_sms_obj(partner)
        promo = partner_fixtures.create_partner_promo_obj(partner=partner)
        promo.last_run = date.today() - timedelta(weeks=2)
        promo.save()
        partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        return sms.per_sms_rate

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

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_send_out_promos__unverified_promo(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        promo = partner_fixtures.create_partner_promo_obj(partner=partner)
        promo.last_run = date.today() - timedelta(weeks=2)
        promo.verified = False
        promo.save()
        partner_fixtures.create_partner_promo_optin_obj(partner=partner)

        send_out_promos()

        assert not mock_send_sms.called

    def test_partner_sms_package_create(self) -> None:
        data = partner_fixtures.partner_sms_fixture(str(self.owner.partner_id), False)

        res = self.authed_client.post(
            f"/{API_VER}/partner/sms/", data=data, format="json"
        )

        assert res.status_code == 200
        assert not res.json()["verified"]
        assert not res.json()["sms_limit"]

    def test_partner_sms_package_read(self) -> None:
        sms = partner_fixtures.create_partner_sms_obj(partner=self.owner.partner)

        res = self.authed_client.get(f"/{API_VER}/partner/sms/{sms.id}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(sms.id)

    def test_create_promo(self) -> None:
        data = partner_fixtures.partner_promo_fixture(
            partner_id=str(self.owner.partner.id)
        )

        res = self.authed_client.post(
            f"/{API_VER}/partner/promo/", data=data, format="json"
        )

        assert res.status_code == 200
        assert res.json()["partner_id"] == str(self.owner.partner.id)

    def test_update_promo(self) -> None:
        promo = partner_fixtures.create_partner_promo_obj(partner=self.owner.partner)
        update_data = {"message": random_string()}

        res = self.authed_client.put(
            f"/{API_VER}/partner/promo/{str(promo.id)}/",
            data=update_data,
            format="json",
        )

        assert res.status_code == 200
        assert res.json()["message"] == update_data["message"]

        promo = partner_fixtures.create_partner_promo_obj()
        update_data = {"message": random_string()}

        res = self.authed_client.put(
            f"/{API_VER}/partner/promo/{str(promo.id)}/",
            data=update_data,
            format="json",
        )
        assert res.status_code == 404

    def test_list_promo(self) -> None:
        partner_fixtures.create_partner_promo_obj(partner=self.owner.partner)
        partner_fixtures.create_partner_promo_obj()

        res = self.authed_client.get(f"/{API_VER}/partner/promo/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_read_promo(self) -> None:
        promo = partner_fixtures.create_partner_promo_obj(partner=self.owner.partner)

        res = self.authed_client.get(f"/{API_VER}/partner/promo/{str(promo.id)}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(promo.id)

        promo = partner_fixtures.create_partner_promo_obj()

        res = self.authed_client.get(f"/{API_VER}/partner/promo/{str(promo.id)}/")

        assert res.status_code == 404

    def test_get_optin_count(self) -> None:
        person = partner_fixtures.create_person_obj()
        partner_fixtures.create_partner_promo_optin_obj(person, self.owner.partner)
        partner_fixtures.create_partner_promo_optin_obj()

        res = self.authed_client.get(
            f"/{API_VER}/partner/promo/optin/count/{str(self.owner.partner.id)}/"
        )

        assert res.status_code == 200
        assert res.json()["count"] == 1

    def test_reconciliation_method(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        event = event_fixtures.create_event_object(partner.owner)
        t1 = ticket_fixtures.create_ticket_obj(event=event)
        t2 = ticket_fixtures.create_ticket_obj(event=event)

        assert partner_service.balance(str(partner.id)) == (
            t1.payment.amount + t2.payment.amount
        )

    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_reconciliation(self, mock_send_sms: Any) -> None:
        partner = partner_fixtures.create_partner_obj()
        partner_fixtures.create_partner_sms_obj(partner=partner)
        event = event_fixtures.create_event_object(partner.owner)
        t1 = ticket_fixtures.create_ticket_obj(event=event)
        t2 = ticket_fixtures.create_ticket_obj(event=event)
        owner = owner_fixtures.create_owner_obj()

        totals = t1.payment.amount + t2.payment.amount
        totals -= self.send_out_promo_util(partner)

        reconcile_payments()

        calls = [
            mock.call(
                args=(
                    partner.owner.phone_number,
                    settings.POST_RECONCILIATION_MESSAGE.format(
                        partner.owner.name, totals
                    ),
                ),
                queue=mock.ANY,
            ),
            mock.call(
                args=(
                    owner.phone_number,
                    f"Your weekly leverage for {date.today()} "
                    f"is {(totals*(partner.comission_rate/100))*(owner.stake/100)}",
                ),
                queue=mock.ANY,
            ),
        ]

        mock_send_sms.assert_has_calls(calls, any_order=True)

    def test_get_partner_revenue(self) -> None:
        partner = partner_fixtures.create_partner_obj()
        event = event_fixtures.create_event_object(owner=partner.owner)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(partner.owner)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.unauthed_client.get(
            f"/{API_VER}/partner/revenue/",
            HTTP_AUTHORIZATION=partner_fixtures.get_partner_owner_auth(partner),
        )

        assert res.status_code == 200
        assert "expenses" in res.json()
        assert "revenue" in res.json()
        assert "net" in res.json()
        revenues = res.json()
        assert revenues["revenue"] == payment.amount
        assert revenues["expenses"] == 0
        assert revenues["net"] == payment.amount * (
            (100 - partner.comission_rate) / 100
        )

    @mock.patch("partner.utils.random_password")
    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_create_verify_otp(
        self, mock_send_sms: Any, mock_random_password: Any
    ) -> None:
        otp = random_password()
        mock_random_password.return_value = otp
        person = partner_fixtures.create_person_obj()
        token = person_service.reset_password(person)

        verification = verify_otp(token, otp)

        assert verification[0]
        assert verification[1] == person.phone_number

        token = person_service.reset_password(person)
        verification = verify_otp(token, random_password())

        assert not verification[0]
        mock_send_sms.assert_called()

    @mock.patch("partner.utils.random_password")
    @mock.patch("notifications.utils.send_sms.apply_async")
    def test_reset_password(
        self, mock_send_sms: Any, mock_random_password: Any
    ) -> None:
        otp = random_password()
        mock_random_password.return_value = otp
        person = partner_fixtures.create_person_obj()
        partner_fixtures.create_partner_obj(owner=person)
        reset_payload = {
            "phone_number": person.phone_number,
        }

        res = self.unauthed_client.post(
            f"/{API_VER}/partner/reset/password/", data=reset_payload, format="json"
        )

        assert res.status_code == 200
        assert res.json()["secret"]
        mock_send_sms.assert_called()
        reset_secret = res.json()["secret"]

        new_password = random_string()

        verification_payload = {
            "secret": reset_secret,
            "otp": otp,
            "new_password": new_password,
        }

        res = self.unauthed_client.post(
            f"/{API_VER}/partner/verify/otp/", data=verification_payload, format="json"
        )

        assert res.status_code == 200
        assert res.json()["token"]
        person.refresh_from_db()
        assert verify_password(new_password, person.hashed_password)

        # with invalid OTP
        verification_payload = {
            "secret": reset_secret,
            "otp": random_password(),
            "new_password": new_password,
        }

        res = self.unauthed_client.post(
            f"/{API_VER}/partner/verify/otp/", data=verification_payload, format="json"
        )

        assert res.status_code == 400
