from core.services import CRUDService
from partner.models import Partner, Person
from partner.serializers import (
    PartnerSerializer,
    PartnerUpdateSerializer,
    PersonCreateSerializer,
    PersonUpdateSerializer,
)
from partner.utils import hash_password


class PersonService(
    CRUDService[Person, PersonCreateSerializer, PersonUpdateSerializer]
):
    def on_pre_create(self, obj_in: PersonCreateSerializer) -> None:
        obj_in.hashed_password = hash_password(obj_in.hashed_password)  # type: ignore


person_service = PersonService(Person)


class PartnerService(CRUDService[Partner, PartnerSerializer, PartnerUpdateSerializer]):
    pass


partner_service = PartnerService(Partner)
