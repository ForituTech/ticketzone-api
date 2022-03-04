from typing import Tuple

from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.services import CRUDService
from partner.models import Partner, Person
from partner.serializers import (
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
    def on_pre_create(self, obj_in: PersonCreateSerializer) -> None:
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
    pass


partner_service = PartnerService(Partner)
