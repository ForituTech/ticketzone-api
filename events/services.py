import uuid
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from rest_framework import status

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.services import CRUDService
from events.models import Event, EventPromotion, TicketPromotion, TicketType
from events.serializers import (
    EventPromotionCreateSerializer,
    EventPromotionUpdateSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TicketTypeCreateSerializer,
    TicketTypePromotionCreateSerializer,
    TicketTypePromotionUpdateSerializer,
    TicketTypeUpdateSerializer,
)
from partner.models import Partner


class EventService(CRUDService[Event, EventSerializer, EventUpdateSerializer]):
    def on_pre_create(self, obj_in: EventSerializer) -> None:
        try:
            partner = Partner.objects.get(pk=obj_in.partner)
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Partner", str(obj_in.partner))
        obj_in.validated_data["partner"] = partner

    def get_partner_events(self, partner_id: uuid.UUID) -> QuerySet[Event]:
        return Event.objects.filter(partner=partner_id)

    def get_event_ticket_types(
        self, event_id: uuid.UUID, **filters: Dict[str, Any]
    ) -> QuerySet[TicketType]:
        return TicketType.objects.filter(event=event_id).filter(**filters)

    # def get_event_promotions()


event_service = EventService(Event)


class TicketTypeService(
    CRUDService[TicketType, TicketTypeCreateSerializer, TicketTypeUpdateSerializer]
):
    def on_pre_create(self, obj_in: TicketTypeCreateSerializer) -> None:
        try:
            event = Event.objects.get(pk=obj_in.event)
        except Event.DoesNotExist:
            raise ObjectNotFoundException("Event", str(obj_in.event))
        obj_in.validated_data["event"] = event

    def get_ticket_types_for_event(self, event_id: str) -> List[TicketType]:
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise HttpErrorException(
                status.HTTP_404_NOT_FOUND, ErrorCodes.INVALID_EVENT_ID
            )
        return list(TicketType.objects.filter(event=event))

    def get_ticket_price_totals(self, ticket_types: Dict[uuid.UUID, int]) -> int:
        total_price: int = 0
        for ticket_type_id, multiplier in ticket_types.items():
            ticket_type = TicketType.objects.get(pk=ticket_type_id)
            total_price += ticket_type.price * multiplier

        return total_price


ticket_type_service = TicketTypeService(TicketType)


class EventPromotionService(
    CRUDService[
        EventPromotion, EventPromotionCreateSerializer, EventPromotionUpdateSerializer
    ]
):
    def on_pre_create(self, obj_in: EventPromotionCreateSerializer) -> None:
        try:
            Event.objects.get(pk=obj_in.event)
        except Event.DoesNotExist:
            raise ObjectNotFoundException("Event", pk=str(obj_in.event))


event_promo_service = EventPromotionService(EventPromotion)


class TicketTypePromotionService(
    CRUDService[
        TicketPromotion,
        TicketTypePromotionCreateSerializer,
        TicketTypePromotionUpdateSerializer,
    ]
):
    def on_pre_create(self, obj_in: TicketTypePromotionCreateSerializer) -> None:
        try:
            TicketType.objects.get(pk=obj_in.ticket)
        except TicketType.DoesNotExist:
            raise ObjectNotFoundException("TicketType", pk=str(obj_in.ticket))


ticket_type_promo_service = TicketTypePromotionService(TicketPromotion)
