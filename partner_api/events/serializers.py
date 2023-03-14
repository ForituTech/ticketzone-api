from datetime import date, time
from typing import Any, List, Optional, Text
from uuid import UUID

from pydantic import BaseModel, validator
from pydantic.fields import ModelField

from partner_api.serializers import InDBBaseSerializer


class TicketTypeSerializer(BaseModel):
    name: str
    price: float
    active: bool
    amsg: Text
    amount: int
    is_visible: bool
    use_limit: int


class PersonSerializer(InDBBaseSerializer):
    name: str
    email: str
    phone_number: str
    person_type: str


class CategorySerializer(InDBBaseSerializer):
    name: str


class EventSerializer(InDBBaseSerializer):
    name: str
    event_number: str
    poster: str
    event_date: date
    time: time
    event_end_date: date
    end_time: time  # type: ignore[valid-type]
    event_location: str
    description: Text
    partner_id: UUID
    category_id: UUID
    event_state: str
    tickets_sold: int
    redemption_rate: float
    sales: float
    assigned_ticketing_agents: Optional[List[PersonSerializer]]
    ticket_types: Optional[List[TicketTypeSerializer]]
    category: CategorySerializer

    @validator("*", pre=True)
    def convert_from_basemanager(cls, value: Any, field: ModelField) -> object:
        list_types = ["assigned_ticketing_agents", "ticket_types"]
        if field.name in list_types and not value:
            return None
        if field.name == "poster":
            if not isinstance(value, str):
                return value.url
        return value
