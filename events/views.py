from typing import Union

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from events.serializers import (EventReadSerializer, EventSerializer,
                                EventUpdateSerializer,
                                TicketTypeCreateSerializer,
                                TicketTypeUpdateSerializer,
                                TickeTypeReadSerializer)
from events.services import event_service, ticket_type_service


@api_view(["GET"])
def list_events(request: Request):
    filters = request.query_params.dict()
    events = event_service.get_filtered(filters=filters)
    return Response(EventReadSerializer(events, many=True).data)


@api_view(["GET"])
def get_event(request: Request, event_id: Union[str, int]):
    obj = event_service.get(pk=event_id)
    if not obj:
        raise HttpErrorException(
            status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_EVENT_ID
        )
    return Response(EventReadSerializer(obj).data)


@api_view(["POST"])
def create_event(request: Request):
    event = event_service.create(obj_data=request.data, serializer=EventSerializer)
    return Response(EventReadSerializer(event).data)


@api_view(["PUT"])
def update_event(request: Request):
    event = event_service.update(
        obj_data=request.data, serializer=EventUpdateSerializer
    )
    return Response(EventReadSerializer(event).data)


@api_view(["GET"])
def list_ticket_types(request: Request, event_id: int):
    ticket_types = ticket_type_service.get_ticket_types_for_event(event_id=event_id)
    return Response(TickeTypeReadSerializer(ticket_types, many=True).data)


@api_view(["POST"])
def create_ticket_type(request: Request):
    ticket_type = ticket_type_service.create(
        obj_data=request.data, serializer=TicketTypeCreateSerializer
    )
    return Response(TickeTypeReadSerializer(ticket_type, many=True).data)


@api_view(["PUT"])
def update_ticket_type(request: Request):
    event = event_service.update(
        obj_data=request.data, serializer=TicketTypeUpdateSerializer
    )
    return Response(EventReadSerializer(event).data)


@api_view(["DELETE"])
def delete_ticket_type(request: Request, event_id: int):
    ticket_type_service.remove()
    raise HttpErrorException(
        status_code=status.HTTP_200_OK, code=ErrorCodes.TICKET_TYPE_OBJECT_DELETED
    )
