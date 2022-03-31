from typing import Any, Dict, List, Tuple

from django.db.models.query import QuerySet
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.services import CRUDService
from events.models import Event
from partner.models import (
    Partner,
    PartnerPerson,
    PartnerPromotion,
    PartnerSMS,
    Person,
    PromoOptIn,
)
from partner.serializers import (
    PartnerPersonCreateSerializer,
    PartnerPersonUpdateSerializer,
    PartnerPromoCreateSerializer,
    PartnerPromoUpdateSerializer,
    PartnerSerializer,
    PartnerSMSPackageCreateSerializer,
    PartnerSMSPackageUpdateSerializer,
    PartnerUpdateSerializer,
    PersonCreateSerializer,
    PersonUpdateSerializer,
    UserSerializer,
)
from partner.utils import hash_password
from tickets.models import Ticket


class PersonService(
    CRUDService[Person, PersonCreateSerializer, PersonUpdateSerializer]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        obj_in["hashed_password"] = hash_password(obj_in["hashed_password"])

    def on_pre_update(self, obj_in: PersonUpdateSerializer, obj: Person) -> None:
        obj_in.hashed_password = hash_password(obj_in.hashed_password)  # type: ignore

    def get_by_phonenumber(self, request: Request) -> Tuple[Person, UserSerializer]:
        credential_error_exception = HttpErrorException(
            status_code=404,
            code=ErrorCodes.INVALID_CREDENTIALS,
        )
        user_in = UserSerializer(data=request.data)
        if not user_in.is_valid():
            raise credential_error_exception
        try:
            user = Person.objects.get(phone_number=user_in.data["phone_number"])
        except Person.DoesNotExist:
            raise credential_error_exception
        except Person.MultipleObjectsReturned:
            raise credential_error_exception
        return (user, user_in)


person_service = PersonService(Person)


class PartnerService(CRUDService[Partner, PartnerSerializer, PartnerUpdateSerializer]):
    def get_total_sales(self, partner_id: str) -> int:
        filters = {
            "ticket_type__event__partner_id": partner_id,
        }
        tickets: int = Ticket.objects.filter(**filters).count()
        return tickets

    def get_total_sales_revenue(self, partner_id: str) -> Dict[str, float]:
        filters = {
            "ticket_type__event__partner_id": partner_id,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters).distinct()
        partner: Partner = Partner.objects.get(id=partner_id)
        sales_total = 0.0
        for ticket in tickets:
            sales_total += ticket.payment.amount

        expenses = 0.0
        try:
            sms: PartnerSMS = PartnerSMS.objects.get(partner_id=partner_id)
            sms_cost = sms.sms_used * sms.per_sms_rate
            expenses += sms_cost
        except PartnerSMS.DoesNotExist:
            pass
        return {
            "revenue": sales_total,
            "net": (100 - partner.comission_rate) / 100 * sales_total,
            "expenses": expenses,
        }

    def get_ranked_events_by_sales(self, partner_id: str) -> List[Event]:
        filters = {
            "partner_id": partner_id,
        }
        return sorted(
            Event.objects.filter(**filters), key=lambda event: (-1 * event.sales)
        )

    def get_total_redemtion_rate(self, partner_id: str) -> float:
        filters = {
            "partner_id": partner_id,
        }
        events: QuerySet[Event] = Event.objects.filter(**filters)
        return sum([event.redemtion_rate for event in events]) / len(events)

    def add_promo_opt_in(self, partner_id: str, person_id: str) -> None:
        try:
            Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Partner", partner_id)
        try:
            Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            raise ObjectNotFoundException("Person", person_id)
        PromoOptIn.objects.create(
            partner_id=partner_id,
            person_id=person_id,
        )

    def promo_optin_count(self, partner_id: str) -> int:
        return PromoOptIn.objects.filter(partner_id=partner_id).count()

    def balance(self, partner_id: str) -> float:
        ticket_filter = {
            "ticket_type__event__partner_id": partner_id,
            "payment__reconciled": False,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**ticket_filter).distinct(
            "payment"
        )
        total_revenue = 0.0
        for ticket in tickets:
            total_revenue += ticket.payment.amount
            ticket.payment.reconciled = True
            ticket.payment.save()
        try:
            sms: PartnerSMS = PartnerSMS.objects.get(partner_id=partner_id)
            sms_cost = sms.sms_used * sms.per_sms_rate
            total_revenue -= sms_cost
        except PartnerSMS.DoesNotExist:
            pass
        return total_revenue


partner_service = PartnerService(Partner)


class PartnerPersonService(
    CRUDService[
        PartnerPerson, PartnerPersonCreateSerializer, PartnerPersonUpdateSerializer
    ]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        obj_in["person_id"] = str(
            person_service.create(
                obj_data=obj_in["person"], serializer=PersonCreateSerializer
            ).id
        )
        del obj_in["person"]


partner_person_service = PartnerPersonService(PartnerPerson)


class PartnerSMSPackageSerivce(
    CRUDService[
        PartnerSMS, PartnerSMSPackageCreateSerializer, PartnerSMSPackageUpdateSerializer
    ]
):
    pass


partner_sms_service = PartnerSMSPackageSerivce(PartnerSMS)


class PartnerPromoService(
    CRUDService[
        PartnerPromotion, PartnerPromoCreateSerializer, PartnerPromoUpdateSerializer
    ]
):
    def on_pre_update(
        self, obj_in: PartnerPromoUpdateSerializer, obj: PartnerPromotion
    ) -> None:
        if obj_in.message:
            obj.verified = False
            obj.save()


partner_promo_service = PartnerPromoService(PartnerPromotion)
