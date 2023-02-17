import uuid
from typing import Any, Optional
from unittest import mock
from unittest.mock import Mock

from django.test import TestCase
from rest_framework.test import APIClient

from eticketing_api import settings
from events.fixtures import event_fixtures
from partner.constants import PersonType
from partner.fixtures import partner_fixtures
from payments.constants import PaymentProviders, PaymentStates
from payments.fixtures import payment_fixtures
from payments.intergrations.ipay import iPayCard, iPayMPesa

API_VER = settings.API_VERSION_STRING


@mock.patch.object(iPayMPesa, "c2b_receive")
@mock.patch.object(iPayCard, "c2b_receive")
class PaymentTestCase(TestCase):
    def setUp(self) -> None:
        self.owner = partner_fixtures.create_partner_person(
            person_type=PersonType.OWNER
        )
        auth_header = {
            settings.AUTH_HEADER: partner_fixtures.create_access_token(
                self.owner.person
            )
        }
        self.client = APIClient(False, **auth_header)
        self.unauthed_client = APIClient(
            False,
        )

    def test_create_payment(self, *args: Optional[Any]) -> None:
        payment_data = payment_fixtures.payment_create_fixture(person=self.owner.person)

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 200
        assert res.json()["person_id"] == str(self.owner.person.id)

    def test_create_payment__inavlid_ticket_type(self, *args: Optional[Any]) -> None:
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[{"id": uuid.uuid4(), "amount": 1}],
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 400

    def test_list_payment_methods(self, *args: Optional[Any]) -> None:
        payment_method = payment_fixtures.create_payment_method_obj()

        res = self.client.get(f"/{API_VER}/payments/methods/", format="json")

        assert res.status_code == 200
        returned_payment_method_names = [method["name"] for method in res.json()]
        assert payment_method.name in returned_payment_method_names

    def test_cant_bundle_unrelated_ticket_types(self, *args: Optional[Any]) -> None:
        ticket_type_1 = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        ticket_type_2 = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[
                {"id": ticket_type_1.id, "amount": 1},
                {"id": ticket_type_2.id, "amount": 1},
            ],
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 400

    def test_create_payment__with_promocode(self, *args: Optional[Any]) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        promo_id = str(event_fixtures.create_event_promo_obj(ticket_type.event).id)
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[{"id": ticket_type.id, "amount": 1}],
            promo=promo_id,
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )
        assert res.status_code == 200
        payment = res.json()
        assert payment["amount"] == 10800.00

        # invalid promocode
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[{"id": ticket_type.id, "amount": 1}],
            promo=str(uuid.uuid4()),
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 404

    def test_create_payment__ticket_type_validations(
        self, *args: Optional[Any]
    ) -> None:
        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person, ticket_types=[{"id": ticket_type.id, "amount": 1}]
        )
        pre_create_amount = ticket_type.amount

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 200
        ticket_type.refresh_from_db()
        assert ticket_type.amount == pre_create_amount - 1

        ticket_type = event_fixtures.create_ticket_type_obj(owner=self.owner.person)
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person,
            ticket_types=[{"id": ticket_type.id, "amount": ticket_type.amount + 1}],
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 400
        assert (
            f"The ticket {ticket_type.name} has only {ticket_type.amount} left"
            in res.json()["detail"]
        )

        ticket_type.amount = 0
        ticket_type.save()
        assert ticket_type.amount == 0
        payment_data = payment_fixtures.payment_create_fixture(
            person=self.owner.person, ticket_types=[{"id": ticket_type.id, "amount": 1}]
        )

        res = self.client.post(
            f"/{API_VER}/payments/", data=payment_data, format="json"
        )

        assert res.status_code == 400
        assert (
            f"The ticket {ticket_type.name} has just sold out :("
            in res.json()["detail"]
        )

    @mock.patch.object(iPayMPesa, "create_partner_owner_payment")
    def test_fund_sms_package(
        self, mock_payment_create: Mock, *args: Optional[Any]
    ) -> None:
        sms_package = partner_fixtures.create_partner_sms_obj(self.owner.partner)
        pre_purchase_sms = sms_package.sms_limit
        payment = payment_fixtures.create_payment_object(
            self.owner.person, amount=sms_package.per_sms_rate * 10
        )
        payment.state = PaymentStates.PAID.value
        payment.save()
        mock_payment_create.return_value = payment

        res = self.client.post(
            f"/{API_VER}/payments/fund/sms/package/",
            data={
                "amount": sms_package.per_sms_rate * 10,
                "made_through": PaymentProviders.MPESA.value,
            },
            format="json",
        )
        assert res.status_code == 200
        assert res.json()["sms_limit"] == pre_purchase_sms + 10
