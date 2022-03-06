from typing import Union

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.views import AbstractPermissionedView
from events.serializers import (
    EventPromotionCreateSerializer,
    EventPromotionReadSerializer,
    EventPromotionUpdateSerializer,
    EventReadSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TicketTypeCreateSerializer,
    TicketTypePromotionCreateSerializer,
    TicketTypePromotionReadSerializer,
    TicketTypePromotionUpdateSerializer,
    TicketTypeUpdateSerializer,
    TickeTypeReadSerializer,
)
from events.services import (
    event_promo_service,
    event_service,
    ticket_type_promo_service,
    ticket_type_service,
)
from partner.permissions import (
    PartnerMembershipPermissions,
    PartnerOwnerPermissions,
    check_self,
    get_request_user_id,
)

paginator = PageNumberPagination()
paginator.page_size = 15


@api_view(["GET"])
def search_events(request: Request, search_term: str) -> Response:
    events = event_service.search(search_term=search_term)
    paginated_events = paginator.paginate_queryset(events, request=request)
    return paginator.get_paginated_response(
        EventReadSerializer(paginated_events, many=True).data
    )


class EventViewset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerOwnerPermissions],
        "update": [PartnerOwnerPermissions],
    }

    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        events = event_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        paginated_events = paginator.paginate_queryset(events, request=request)
        return paginator.get_paginated_response(
            EventReadSerializer(paginated_events, many=True).data
        )

    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        event = event_service.get(pk=pk)
        if not event:
            raise HttpErrorException(
                status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_EVENT_ID
            )
        return Response(EventReadSerializer(event).data)

    def create(self, request: Request) -> Response:
        event = event_service.create(obj_data=request.data, serializer=EventSerializer)
        # TODO: check_self before event creation
        try:
            check_self(request, str(event.partner.owner.id))
        except Exception as exc:
            event.delete()
            raise exc
        return Response(EventReadSerializer(event).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        event = event_service.get(pk=pk)
        if not event:
            raise ObjectNotFoundException("Event", str(pk))
        check_self(request, str(event.partner.owner.id))
        event = event_service.update(
            obj_data=request.data, serializer=EventUpdateSerializer, obj_id=pk
        )
        return Response(EventReadSerializer(event).data)


class TicketTypeViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerMembershipPermissions],
        "update": [PartnerMembershipPermissions],
    }

    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        if not filters or "event_id" not in filters:
            raise HttpErrorException(
                status_code=status.HTTP_403_FORBIDDEN,
                code=ErrorCodes.GENERIC_TICKET_TYPE_LISTING,
            )
        ticket_types = ticket_type_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        paginated_tickets = paginator.paginate_queryset(ticket_types, request=request)
        return paginator.get_paginated_response(
            TickeTypeReadSerializer(paginated_tickets, many=True).data
        )

    def create(self, request: Request) -> Response:
        ticket_type = ticket_type_service.create(
            obj_data=request.data, serializer=TicketTypeCreateSerializer
        )
        # TODO: check_self before ticket_type creation
        try:
            check_self(request, str(ticket_type.event.partner.owner.id))
        except Exception as exc:
            ticket_type.delete()
            raise exc
        return Response(TickeTypeReadSerializer(ticket_type).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        ticket_type = ticket_type_service.update(
            obj_data=request.data, serializer=TicketTypeUpdateSerializer, obj_id=pk
        )
        if not ticket_type:
            raise ObjectNotFoundException("Event", str(pk))
        check_self(request, str(ticket_type.event.partner.owner.id))
        return Response(EventReadSerializer(ticket_type).data)


class TicketTypePromotionViewset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerMembershipPermissions],
        "update": [PartnerMembershipPermissions],
        "list": [PartnerOwnerPermissions],
    }

    def create(self, request: Request) -> Response:
        ticket_promo = ticket_type_promo_service.create(
            obj_data=request.data,
            serializer=TicketTypePromotionCreateSerializer,
        )
        try:
            check_self(request, str(ticket_promo.ticket.event.partner.owner.id))
        except Exception as exc:
            ticket_promo.delete()
            raise exc
        return Response(TicketTypePromotionReadSerializer(ticket_promo).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        ticket_promo = ticket_type_promo_service.get(pk=pk)
        if not ticket_promo:
            raise ObjectNotFoundException("Ticket Promotion", str(pk))
        check_self(request, str(ticket_promo.ticket.event.partner.owner.id))
        ticket_promo = ticket_type_promo_service.update(
            obj_data=request.data,
            serializer=TicketTypePromotionUpdateSerializer,
            obj_id=pk,
        )
        return Response(TicketTypePromotionReadSerializer(ticket_promo).data)

    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        if not filters:
            filters = {}
        filters["ticket__event__partner__owner_id"] = get_request_user_id(request)
        ticket_promos = ticket_type_promo_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        ticket_promos_page = paginator.paginate_queryset(ticket_promos, request=request)
        return paginator.get_paginated_response(
            TicketTypePromotionReadSerializer(ticket_promos_page, many=True).data
        )


class EventPromotionViewset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerOwnerPermissions, PartnerMembershipPermissions],
        "update": [PartnerOwnerPermissions, PartnerMembershipPermissions],
        "list": [PartnerOwnerPermissions],
    }

    def create(self, request: Request) -> Response:
        event_promo = event_promo_service.create(
            obj_data=request.data,
            serializer=EventPromotionCreateSerializer,
        )
        try:
            check_self(request, str(event_promo.event.partner.owner.id))
        except Exception as exc:
            event_promo.delete()
            raise exc
        return Response(EventPromotionReadSerializer(event_promo).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        event_promo = event_promo_service.get(pk=pk)
        if not event_promo:
            raise ObjectNotFoundException("Event Promotion", str(pk))
        check_self(request, str(event_promo.event.partner.owner.id))
        event_promo = event_promo_service.update(
            obj_data=request.data, serializer=EventPromotionUpdateSerializer, obj_id=pk
        )
        return Response(EventPromotionReadSerializer(event_promo).data)

    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        if not filters:
            filters = {}
        filters["event__partner__owner_id"] = get_request_user_id(request)
        event_promos = event_promo_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        event_promos_list = paginator.paginate_queryset(event_promos, request=request)
        return paginator.get_paginated_response(
            EventPromotionReadSerializer(event_promos_list, many=True).data
        )
