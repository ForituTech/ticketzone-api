from typing import Dict, List

from rest_framework import status

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.services import CRUDService
from events.models import Event, EventPromotion, TicketPromotion, TicketType
from events.serializers import (
    EventPromotionSerializer,
    EventPromotionUpdateSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TicketTypeCreateSerializer,
    TicketTypePromotionSerializer,
    TicketTypePromotionUpdateSerializer,
    TicketTypeUpdateSerializer,
)
from partner.models import Partner


class EventService(CRUDService[Event, EventSerializer, EventUpdateSerializer]):
    def on_pre_create(self, obj_in: EventSerializer) -> None:
        try:
            partner = Partner.objects.get(pk=obj_in.partner)
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Partner", obj_in.partner)
        obj_in.validated_data["partner"] = partner

    def get_partner_events(self, partner_id: int, **filters):
        return Event.objects.filter(partner=partner_id)

    def get_event_ticket_types(self, event_id: int, **filters):
        return TicketType.objects.filter(event=event_id).filter(**filters)

    # def get_event_promotions()


event_service = EventService(Event)


class TicketTypeService(
    CRUDService[TicketType, TicketTypeCreateSerializer, TicketTypeUpdateSerializer]
):
    def get_ticket_types_for_event(self, event_id: str) -> List[TicketType]:
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise HttpErrorException(
                status.HTTP_404_NOT_FOUND, ErrorCodes.INVALID_EVENT_ID
            )
        return TicketType.objects.filter(event=event)

    def get_ticket_price_totals(self, ticket_types: Dict[int, int]) -> int:
        total_price: int = 0
        for ticket_type_id, multiplier in enumerate(ticket_types):
            ticket_type = TicketType.objects.get(pk=ticket_type_id)
            total_price += ticket_type.price * multiplier

        return total_price


ticket_type_service = TicketTypeService(TicketType)


class EventPromotionService(
    CRUDService[
        EventPromotion, EventPromotionSerializer, EventPromotionUpdateSerializer
    ]
):
    def on_pre_create(self, obj_in: EventPromotionSerializer) -> None:
        try:
            Event.objects.get(pk=obj_in.event)
        except Event.DoesNotExist:
            raise ObjectNotFoundException("Event", pk=obj_in.event)


event_promo_service = EventPromotionService(EventPromotion)


class TicketTypePromotionService(
    CRUDService[
        TicketPromotion,
        TicketTypePromotionSerializer,
        TicketTypePromotionUpdateSerializer,
    ]
):
    def on_pre_create(self, obj_in: TicketTypePromotionSerializer) -> None:
        try:
            TicketType.objects.get(pk=obj_in.ticket)
        except TicketType.DoesNotExist:
            raise ObjectNotFoundException("TicketType", pk=obj_in.ticket)


ticket_type_promo_service = TicketTypePromotionService(TicketPromotion)
