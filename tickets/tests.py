from datetime import datetime, timedelta

from django.test import Client, TestCase
from rest_framework.test import APIClient

from eticketing_api import settings
from events.fixtures import event_fixtures
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from partner.fixtures.partner_fixtures import create_auth_token
from partner.utils import create_access_token_lite
from payments.fixtures import payment_fixtures
from tickets.fixtures import ticket_fixtures
from tickets.models import Ticket
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

    def test_create_ticket(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)

        ticket_data = ticket_fixtures.ticket_fixture(
            ticket_type_id=str(ticket_type.id), payment_id=str(payment.id)
        )

        res = self.li_client.post(
            f"/{API_VER}/tickets/", data=ticket_data, format="json"
        )
        assert res.status_code == 200
        returned_ticket = res.json()
        assert returned_ticket["ticket_type_id"] == str(ticket_type.id)
        assert returned_ticket["payment_id"] == str(payment.id)

        ticket_from_db: Ticket = Ticket.objects.get(pk=returned_ticket["id"])
        assert ticket_from_db.hash
        assert ticket_from_db.hash == compute_ticket_hash(ticket_from_db)

    def test_create_ticket__not_self(self) -> None:
        ticket_data = ticket_fixtures.ticket_fixture()

        res = self.li_client.post(
            f"/{API_VER}/tickets/", data=ticket_data, format="json"
        )

        assert res.status_code == 403

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

    def test_tickets_export(self) -> None:
        event = event_fixtures.create_event_object(self.owner.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket_fixtures.create_ticket_obj()

        res = self.client.get(f"/{API_VER}/tickets/export/csv/")
        assert res.status_code == 200

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

    def test_ticket_read_by_hash(self) -> None:
        event = event_fixtures.create_event_object(self.person)
        ticket_type = event_fixtures.create_ticket_type_obj(event=event)
        payment = payment_fixtures.create_payment_object(self.person)
        ticket = ticket_fixtures.create_ticket_obj(ticket_type, payment)
        ticket.hash = compute_ticket_hash(ticket)
        ticket.save()

        res = self.client.get(f"/{API_VER}/tickets/by/hash/{ticket.hash}/")

        assert res.status_code == 200
        assert res.json()["id"] == str(ticket.id)

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

        res = self.client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 1

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

        res = self.client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 1

        res = self.client.post(f"/{API_VER}/tickets/redeem/{ticket.id}/")

        assert res.status_code == 200
        assert res.json()["uses"] == 2

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
