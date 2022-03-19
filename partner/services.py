from typing import Any, Dict, List, Tuple

from django.db.models.query import QuerySet
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.services import CRUDService
from events.models import Event
from partner.models import (
    Partner,
    PartnerBankingInfo,
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
    def on_relationship_update(self, obj_data: Dict[str, Any], obj: Partner) -> None:
        PartnerBankingInfo.objects.filter(pk=str(obj.banking_info.id)).update(
            **obj_data["banking_info"]
        )
        obj_data["banking_info_id"] = str(obj.banking_info.id)
        del obj_data["banking_info"]

    def get_total_sales(self, partner_id: str) -> float:
        filters = {
            "ticket_type__event__partner_id": partner_id,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters)
        sales_total = 0.0
        for ticket in tickets:
            sales_total += ticket.payment.amount
        return sales_total

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
