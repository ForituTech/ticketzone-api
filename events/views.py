from typing import Union

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.views import AbstractPermissionedView
from events.serializers import (
    EventReadSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TicketTypeCreateSerializer,
    TicketTypeUpdateSerializer,
    TickeTypeReadSerializer,
)
from events.services import event_service, ticket_type_service
from partner.permissions import PartnerPermissions

paginator = PageNumberPagination()
paginator.page_size = 15


class EventVieset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerPermissions],
        "update": [PartnerPermissions],
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
        obj = event_service.get(pk=pk)
        if not obj:
            raise HttpErrorException(
                status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_EVENT_ID
            )
        return Response(EventReadSerializer(obj).data)

    def create(self, request: Request) -> Response:
        event = event_service.create(obj_data=request.data, serializer=EventSerializer)
        return Response(EventReadSerializer(event).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        event = event_service.update(
            obj_data=request.data, serializer=EventUpdateSerializer, obj_id=pk
        )
        return Response(EventReadSerializer(event).data)


class TicketTypeViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerPermissions],
        "update": [PartnerPermissions],
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
        return Response(TickeTypeReadSerializer(ticket_type).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        event = ticket_type_service.update(
            obj_data=request.data, serializer=TicketTypeUpdateSerializer, obj_id=pk
        )
        return Response(EventReadSerializer(event).data)


class TicketTypePromotionViewset(AbstractPermissionedView):
    pass
