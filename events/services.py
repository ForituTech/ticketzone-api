import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Union

from django.db import transaction
from django.db.models import Sum
from django.db.models.query import QuerySet
from rest_framework import status

from core.error_codes import ErrorCodes
from core.exceptions import (
    HttpErrorException,
    ObjectInvalidException,
    ObjectNotFoundException,
)
from core.services import CRUDService
from events.models import (
    Event,
    EventCategory,
    EventPromotion,
    PartnerPersonSchedule,
    ReminderOptIn,
    TicketType,
)
from events.serializers import (
    CategoryInnerSerializer,
    EventPromotionCreateSerializer,
    EventPromotionUpdateSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TicketTypeCreateSerializer,
    TicketTypeUpdateSerializer,
)
from partner.models import Partner, Person


class EventService(CRUDService[Event, EventSerializer, EventUpdateSerializer]):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        try:
            Partner.objects.get(pk=obj_in["partner_id"])
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Partner", str(obj_in["partner_id"]))
        except KeyError:
            raise ObjectInvalidException("Event")

    def on_relationship(
        self, obj_in: Dict[str, Any], obj: Event, create: bool = True
    ) -> None:
        if partner_person_ids := obj_in.get("partner_person_ids", None):
            if isinstance(partner_person_ids, str):
                partner_person_ids = [partner_person_ids]
            for partner_person_id in partner_person_ids:
                try:
                    partner_person_schedule: PartnerPersonSchedule = (
                        PartnerPersonSchedule.objects.get(
                            partner_person_id=partner_person_id
                        )
                    )
                    partner_person_schedule.event = obj
                    partner_person_schedule.save()
                except PartnerPersonSchedule.DoesNotExist:
                    partner_person_schedule = PartnerPersonSchedule.objects.create(
                        event_id=obj.id, partner_person_id=partner_person_id
                    )
                    partner_person_schedule.save()
            # drop all partner persons schedules for persons
            # who aren't in the payload
            PartnerPersonSchedule.objects.exclude(
                partner_person_id__in=partner_person_ids
            ).delete()

        if ticket_types := obj_in.get("ticket_types", None):
            if isinstance(ticket_types, dict):
                ticket_types = [ticket_types]
            accessed_tt_names = []
            for ticket_type in ticket_types:
                filters = {"name": ticket_type["name"], "event_id": str(obj.id)}
                try:
                    TicketType.objects.get(**filters)
                    TicketType.objects.filter(**filters).update(**ticket_type)
                    accessed_tt_names.append(ticket_type["name"])
                except TicketType.DoesNotExist:
                    ticket_type_copy = ticket_type.copy()
                    ticket_type_copy["event_id"] = str(obj.id)
                    TicketType.objects.create(**ticket_type_copy)
                    accessed_tt_names.append(ticket_type["name"])

            TicketType.objects.exclude(
                name__in=accessed_tt_names, event_id=str(obj.id)
            ).update(active=False)
            TicketType.objects.filter(name__in=accessed_tt_names, active=False).update(
                active=True
            )

        if event_promos := obj_in.get("event_promotions", None):
            EventPromotion.objects.filter(event_id=obj.id).delete()
            for event_promo in event_promos:
                event_promo_copy = event_promo.copy()
                event_promo_copy["event_id"] = obj.id
                EventPromotion.objects.create(**event_promo_copy)

    def modify_query(
        self,
        query: QuerySet,
        order_fields: Optional[List] = None,
        filters: Optional[dict] = None,
    ) -> QuerySet:
        if order_fields:
            if "-sales" in order_fields or "sales" in order_fields:
                query = query.annotate(sales=Sum("tickettype__ticket__payment__amount"))

        return query

    def get_partner_events(self, partner_id: Union[uuid.UUID, str]) -> QuerySet[Event]:
        return Event.objects.filter(partner=partner_id)  # type: ignore

    def get_partner_events_count(self, partner_id: uuid.UUID) -> int:
        return Event.objects.filter(partner=partner_id).count()

    def get_event_ticket_types(
        self, event_id: uuid.UUID, **filters: Dict[str, Any]
    ) -> QuerySet[TicketType]:
        return TicketType.objects.filter(event=event_id).filter(**filters)

    def create_reminder_optin(self, person_id: str, event_id: str) -> None:
        try:
            Event.objects.get(id=event_id)
        except Partner.DoesNotExist:
            raise ObjectNotFoundException("Event", event_id)
        try:
            Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            raise ObjectNotFoundException("Person", person_id)
        ReminderOptIn.objects.create(
            person_id=person_id,
            event_id=event_id,
        )

    def get_ta_assigned_events(self, person_id: str) -> List[str]:
        events_schedules = PartnerPersonSchedule.objects.filter(
            partner_person__person_id=person_id
        )
        if not events_schedules:
            event_tickets = TicketType.objects.filter(
                **{"event__partner__owner_id": person_id}
            )
        return [
            str(schedule.event_id) for schedule in events_schedules or event_tickets
        ]

    # def get_event_promotions()


event_service = EventService(Event)


class TicketTypeService(
    CRUDService[TicketType, TicketTypeCreateSerializer, TicketTypeUpdateSerializer]
):
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        try:
            Event.objects.get(pk=obj_in["event_id"])
        except Event.DoesNotExist:
            raise ObjectNotFoundException("Event", str(obj_in["event_id"]))
        except KeyError:
            raise ObjectInvalidException("TicketType")

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
    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        try:
            Event.objects.get(pk=obj_in["event_id"])
        except Event.DoesNotExist:
            raise ObjectNotFoundException("Event", pk=str(obj_in["event_id"]))
        except KeyError:
            raise ObjectInvalidException("EventPromotion")

    def redeem(self, promo: EventPromotion) -> bool:
        if not promo.use_limit:
            return False
        if promo.expiry < date.today():
            return False
        promo.use_limit -= 1
        promo.save()
        return True

    def check(self, promo_code: str, event_id: str) -> Optional[EventPromotion]:
        if EventPromotion.objects.filter(
            event_id=event_id,
            name=promo_code,
            expiry__gte=date.today(),
            use_limit__gt=0,
        ).exists():

            # decrement the promos use limit
            with transaction.atomic():
                promo_locked = EventPromotion.objects.select_for_update().get(
                    name=promo_code, event_id=event_id
                )
                promo_locked.use_limit -= 1
                promo_locked.save()

            return EventPromotion.objects.filter(name=promo_code).first()

        return None


event_promo_service = EventPromotionService(EventPromotion)


class CategoryService(
    CRUDService[EventCategory, CategoryInnerSerializer, CategoryInnerSerializer]
):
    pass


category_service = CategoryService(EventCategory)
