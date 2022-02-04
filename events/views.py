from typing import Union

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectInvalidException
from events.serializers import (EventReadSerializer, EventSerializer,
                                EventUpdateSerializer)
from events.services import event_service


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
            status_code=status.HTTP_404_NOT_FOUND, 
            code=ErrorCodes.INVALID_EVENT_ID
        )
    return Response(EventReadSerializer(obj).data)


@api_view(["POST"])
def create_event(request: Request):
    event_in = EventSerializer(data_in=request.data, data=request.data)
    if not event_in.is_valid(raise_exception=False):
        raise ObjectInvalidException("Event")
    event = event_service.create(obj_in=event_in)
    return Response(EventReadSerializer(event).data)


@api_view(["PUT"])
def update_event(request: Request):
    event_in = EventUpdateSerializer(data_in=request.data, data=request.data)
    if not event_in.is_valid(raise_exception=False):
        raise ObjectInvalidException("Event")
    event = event_service.update(obj_id=event_in.id, obj_in=event_in)
    return Response(EventReadSerializer(event).data)
