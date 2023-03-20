from typing import List, Sequence

from pydantic import AnyUrl, BaseModel, validator

from partner.utils import validate_email, validate_phonenumber
from partner_api.serializers import InDBBaseSerializer


class TicketTypeSerializer(BaseModel):
    id: str
    amount: int


class TicketTypeInnerSerializer(InDBBaseSerializer):
    name: str
    price: float


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
