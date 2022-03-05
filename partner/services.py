from typing import Any, Dict, Tuple

from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from partner.models import Partner, PartnerBankingInfo, PartnerPerson, Person
from partner.serializers import (
    PartnerPersonCreateSerializer,
    PartnerPersonUpdateSerializer,
    PartnerSerializer,
    PartnerUpdateSerializer,
    PersonCreateSerializer,
    PersonUpdateSerializer,
    UserSerializer,
)
from partner.utils import hash_password


class PersonService(
    CRUDService[Person, PersonCreateSerializer, PersonUpdateSerializer]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        obj_in["hashed_password"] = hash_password(obj_in["hashed_password"])

    def on_pre_update(self, obj_in: PersonUpdateSerializer) -> None:
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
