from datetime import datetime, timedelta

from django.test import Client, TestCase
from rest_framework.test import APIClient

from core.utils import random_string
from eticketing_api import settings
from events.fixtures import event_fixtures
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from partner.fixtures.partner_fixtures import create_auth_token
from partner.utils import create_access_token_lite
from payments.fixtures import payment_fixtures
from tickets.fixtures import ticket_fixtures
from tickets.utils import (
    compute_ticket_hash,
    generate_ticket_qr,
    get_ticket_hash_from_qr,
)

API_VER = settings.API_VERSION_STRING


class TicketTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        self.auth_header = {settings.AUTH_HEADER: create_auth_token(self.owner.person)}
        self.client = APIClient(enforce_csrf_checks=False, **self.auth_header)
        # Only logged_in, no partnership
        self.person = partner_fixtures.create_person_obj()
        self.li_authed_header = {
            settings.AUTH_HEADER: create_access_token_lite(user=self.person)
        }
        self.li_client: Client = APIClient(
            enforce_csrf_checks=False, **self.li_authed_header
        )
        # ticketing agent
        self.ta = partner_fixtures.create_partner_person(
            person_type=PersonType.TICKETING_AGENT, partner=self.owner.partner
        )
        self.ta_client: Client = APIClient(
            enforce_csrf_checks=False,
            **{settings.AUTH_HEADER: create_auth_token(self.ta.person)},
        )

    def test_ticket_list(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj()

        res = self.client.get(f"/{API_VER}/tickets/")

        assert res.status_code == 200
        assert res.json()["count"] == 1

        res = self.client.get(f"/{API_VER}/tickets/?page=1")
        res.status_code == 200

        res = self.client.get(f"/{API_VER}/tickets/?per_page=1")
        res.status_code == 200

        res = self.client.get(f"/{API_VER}/tickets/?per_page=a")
        res.status_code == 422

        res = self.client.get(f"/{API_VER}/tickets/?ticket_type__event_id=1")
        assert res.status_code == 422

        res = self.client.get(f"/{API_VER}/tickets/?ordering=-{random_string()}")
        # sort fields should be cleaned
        assert res.status_code == 200

    def test_ticket_pagination(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        for _ in range(0, 20):
            payment = payment_fixtures.create_payment_object()
            ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res1 = self.client.get(f"/{API_VER}/tickets/?page=1&per_page=5")
        assert res1.status_code == 200
        assert len(res1.json()["results"]) == 5
        assert res1.json()["next"]
        returned_ticket_dates = [
            ticket["created_at"] for ticket in res1.json()["results"]
        ]

        res2 = self.client.get(f"/{API_VER}/tickets/?page=2&per_page=5")
        assert res2.status_code == 200
        assert len(res2.json()["results"]) == 5
        assert res2.json()["next"]
        returned_ticket_dates.extend(
            [ticket["created_at"] for ticket in res2.json()["results"]]
        )

        # dependent on the default sorting being created_at
        assert sorted(returned_ticket_dates) == returned_ticket_dates

    def test_tickets_export(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj()

        res = self.client.get(f"/{API_VER}/tickets/export/csv/")
        assert res.status_code == 200
        fields = [
            "created_at",
            "ticket_number",
            "ticket_type.event.name",
            "payment.amount",
        ]
        returned_text = str(res.getvalue())
        for field in fields:
            assert field in returned_text

    def test_ticket_list__non_owner(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.li_client.get(f"/{API_VER}/tickets/")

        assert res.status_code == 403

    def test_ticket_read(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()

        res = self.client.get(f"/{API_VER}/tickets/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(ticket.id)
        assert "poster" in res.json()["ticket_type"]["event"]

    def test_ticket_read_by_hash(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        event_fixtures.create_partner_person_schedule(
            event_id=str(event.id), partner_person_id=str(self.ta.id)
        )
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()

        res = self.ta_client.get(f"/{API_VER}/tickets/by/hash/{ticket.hash}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(ticket.id)

        # read should fail on unrelated events
        event2 = event_fixtures.create_event_object(self.owner.person)
        ticket_type2 = event_fixtures.create_ticket_type_obj(event=event2)
        event_fixtures.create_partner_person_schedule(event_id=str(event2.id))
        payment2 = payment_fixtures.create_payment_object(self.person)
        ticket2 = ticket_fixtures.create_ticket_obj(ticket_type2, payment2)
        ticket2.hash = compute_ticket_hash(ticket2)
        ticket2.save()

        res = self.ta_client.get(f"/{API_VER}/tickets/by/hash/{ticket2.hash}/")

        assert res.status_code == 404

        # should be visible to the event owner
        res = self.client.get(f"/{API_VER}/tickets/by/hash/{ticket2.hash}/")

        assert res.status_code == 200

    def test_ticket_read_by_hash__invalid_hash(self) -> None:
        res = self.client.get(f"/{API_VER}/tickets/by/hash/{123}/")

        assert res.status_code == 404
        assert "UNRESOLVABLE_HASH" in res.json()["detail"]

    def test_ticket_redeem(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()
        ticket.payment.state = "PAID"
        ticket.payment.save()

        res = self.ta_client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 1
        assert res.json()["redeemed"]

        scans_res = self.ta_client.get(f"/{API_VER}/tickets/scan/records/")
        assert scans_res.status_code == 200
        scan_records = scans_res.json()["results"]
        scan_record_ticket_ids = [record["ticket"]["id"] for record in scan_records]
        assert str(ticket.id) in scan_record_ticket_ids

    def test_fetch_scan_records(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()
        ticket.payment.state = "PAID"
        ticket.payment.save()

        res = self.ta_client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200

        scans_res = self.ta_client.get(f"/{API_VER}/tickets/scan/records/")
        assert scans_res.status_code == 200
        scan_records = scans_res.json()["results"]
        scan_record_ticket_ids = [record["ticket"]["id"] for record in scan_records]
        assert str(ticket.id) in scan_record_ticket_ids

        scans_res = self.ta_client.get(
            f"/{API_VER}/tickets/scan/records/?search={ticket.payment.person.name}"
        )
        assert scans_res.status_code == 200
        scan_records = scans_res.json()["results"]
        scan_record_ticket_ids = [record["ticket"]["id"] for record in scan_records]
        assert str(ticket.id) in scan_record_ticket_ids

    def test_ticket_multiple_redeem(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()
        ticket_type.use_limit = 2
        ticket_type.save()
        ticket.payment.state = "PAID"
        ticket.payment.save()

        res = self.ta_client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 1

        res = self.ta_client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 2
        assert res.json()["valid"] == "REDEEMED"

        res = self.client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 403
        assert "REDEEMED_TICKET" in res.json()["detail"]

    def test_ticket_redeem__unpaid(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()

        res = self.client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 403
        assert "UNPAID" in res.json()["detail"]

    def test_ticket_qr_code_gen(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()

        image_str = generate_ticket_qr(ticket)
        image_hash = get_ticket_hash_from_qr(image_str)

        assert image_hash == ticket.hash

    def test_search_tickets(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)

        res = self.client.get(
            f"/{API_VER}/tickets/?page=1&per_page=5&search={ticket.payment.person.name}"
        )

        assert res.status_code == 200
        assert len(res.json()["results"]) == 1
        assert "payment" in res.json()["results"][0]

    def test_ticket_counts_over_time(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        tickets = [
            ticket_fixtures.create_ticket_obj(ticket_type, payment),
            ticket_fixtures.create_ticket_obj(ticket_type, payment),
            ticket_fixtures.create_ticket_obj(ticket_type, payment),
        ]
        tickets[2].created_at = datetime.utcnow() - timedelta(days=1)
        tickets[2].save()
        ticket_fixtures.create_ticket_obj()

        res = self.client.get(f"/{API_VER}/tickets/count/by/date/")

        assert res.status_code == 200
        counts = res.json()["data"]
        counts_without_date = [count["count"] for count in counts]
        assert 2 in counts_without_date
        assert 1 in counts_without_date
