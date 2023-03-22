from typing import List, Optional, Sequence
from uuid import UUID

from pydantic import AnyUrl, BaseModel, validator
from rest_framework.serializers import ImageField

from partner.utils import validate_email, validate_phonenumber
from partner_api.serializers import InDBBaseSerializer
from payments.constants import PaymentProviders


class TicketTypeSerializer(BaseModel):
    id: str
    amount: int


class TicketTypeInnerSerializer(InDBBaseSerializer):
    name: str
    price: float
    amount: int


class PersonSerializer(BaseModel):
    name: str
    email: str
    phone_number: str

    @validator("email")
    def validate_email(cls, email: str) -> str:
        if not validate_email(email):
            raise ValueError("Email is invalid")
        return email

    @validator("phone_number")
    def validate_phone_number(cls, phone: str) -> str:
        if not validate_phonenumber(phone):
            raise ValueError("Phonenumber is invalid")
        return phone


class PersonInDBSerializer(PersonSerializer, InDBBaseSerializer):
    pass


class PaymentIntentCreateSerializer(BaseModel):
    person: PersonSerializer
    ticket_types: List[TicketTypeSerializer]
    callback_url: AnyUrl


class PaymentIntentSerializer(InDBBaseSerializer):
    amount: float
    person: PersonInDBSerializer
    ticket_types: Sequence[TicketTypeInnerSerializer]
    redirect_to: AnyUrl
    event_poster: Optional[str]
    event_id: str

    @validator("event_poster", pre=True)
    def validate_event_poster(cls, value: ImageField) -> str:
        return str(value)


class PaymentCreateSerializer(BaseModel):
    intent_id: UUID
    made_through: PaymentProviders


class PaymentSerializer(InDBBaseSerializer):
    amount: float
    person_id: str
    made_through: str
