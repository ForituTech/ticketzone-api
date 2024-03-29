from http import HTTPStatus
from typing import Union
from uuid import UUID

from django.http import QueryDict, StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVStreamingRenderer, PaginatedCSVRenderer

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException, ObjectNotFoundException
from core.pagination import CustomPagination
from core.serializers import (
    DefaultQuerySerialzier,
    EventCountSerializer,
    VerifyActionSerializer,
)
from core.utils import get_selected_fields, stream_model_data
from core.views import AbstractPermissionedView
from eticketing_api import settings
from events.serializers import (
    CategorySerializer,
    EventBaseSerializer,
    EventPromotionBaseSerializer,
    EventPromotionCreateSerializer,
    EventPromotionReadSerializer,
    EventPromotionSerializer,
    EventPromotionUpdateSerializer,
    EventPromotionValidatedSerializer,
    EventReadSerializer,
    EventSerializer,
    EventUpdateSerializer,
    TickeTypeReadSerializer,
)
from events.services import (
    category_service,
    event_promo_service,
    event_service,
    ticket_type_service,
)
from events.utils import pre_process_data
from partner.permissions import (
    PartnerMembershipPermissions,
    PartnerOwnerPermissions,
    check_self,
    get_request_partner_id,
    get_request_user_id,
)
from partner.utils import (
    get_request_membership_or_ownership,
    get_user_from_access_token,
)

paginator = PageNumberPagination()
paginator.page_size = 15


@swagger_auto_schema(method="get", responses={200: EventReadSerializer(many=True)})
@api_view(["GET"])
def highlighted_events(request: Request) -> Response:
    filters = request.query_params.dict()
    filters["ordering"] = "sales"
    events = event_service.get_filtered(filters=filters, limit=5, paginator=paginator)
    paginated_events = paginator.paginate_queryset(events, request=request)
    return paginator.get_paginated_response(
        EventReadSerializer(paginated_events, many=True).data
    )


@swagger_auto_schema(method="get", responses={200: EventPromotionValidatedSerializer})
@api_view(["GET"])
def validate_promocode(request: Request, event_id: str, code: str) -> Response:
    if promo := event_promo_service.check(event_id=event_id, promo_code=code):
        return Response({"id": str(promo.id), "percent_off": promo.promotion_rate})
    else:
        raise HttpErrorException(
            status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.PROMO_NOT_FOUND
        )


@swagger_auto_schema(method="get", responses={200: CategorySerializer(many=True)})
@api_view(["GET"])
def list_categories(request: Request) -> Response:
    filters = request.query_params.dict()
    categories = category_service.get_filtered(filters=filters)
    return Response(CategorySerializer(categories, many=True).data)


@swagger_auto_schema(method="post", responses={200: VerifyActionSerializer(many=True)})
@api_view(["POST"])
def event_reminder_optin(request: Request, event_id: str) -> Response:
    token_key = settings.AUTH_HEADER
    person_id = get_user_from_access_token(request.META[token_key]).id
    event_service.create_reminder_optin(str(person_id), event_id)
    return Response({"done": True})


@swagger_auto_schema(method="get", responses={200: EventCountSerializer})
@api_view(["GET"])
def get_total_events_for_partner(request: Request, partner_id: str) -> Response:
    count = event_service.get_partner_events_count(partner_id=UUID(partner_id))
    return Response(EventCountSerializer({"count": count}).data)


@swagger_auto_schema(method="get")
@api_view(["GET"])
@permission_classes([PartnerOwnerPermissions])
@renderer_classes([CSVStreamingRenderer])
def export_events(request: Request) -> StreamingHttpResponse:
    # This is dependent on djangos default lazy loading
    # behaviour
    fields = ["event_number", "name", "event_date", "sales"]
    request.accepted_renderer.header = get_selected_fields(request) or fields
    tickets = event_service.get_all()
    response = StreamingHttpResponse(
        request.accepted_renderer.render(
            stream_model_data(queryset=tickets, serializer=EventReadSerializer)
        ),
        status=200,
        content_type="text/csv",
    )
    response["Content-Disposition"] = 'attachment; filename="tickets.csv"'
    return response


class EventViewset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerOwnerPermissions],
        "update": [PartnerOwnerPermissions],
    }
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, JSONParser]
    renderer_classes = (JSONRenderer, PaginatedCSVRenderer)

    @swagger_auto_schema(
        responses={200: EventReadSerializer(many=True)},
        query_serializer=DefaultQuerySerialzier,
    )
    def list(self, request: Request) -> Response:
        try:
            partner_id = get_request_membership_or_ownership(request)[0]
        except HttpErrorException:
            partner_id = ""
        filters = request.query_params.dict()
        filters["partner_id"] = partner_id
        if not partner_id:
            filters["is_public"] = True  # type: ignore[assignment]
        events = event_service.get_filtered(filters=filters, paginator=paginator)
        paginated_events = paginator.paginate_queryset(events, request=request)
        return paginator.get_paginated_response(
            EventReadSerializer(paginated_events, many=True).data
        )

    @swagger_auto_schema(responses={200: EventReadSerializer()})
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        event = event_service.get(pk=pk)
        if not event:
            raise HttpErrorException(
                status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_EVENT_ID
            )
        return Response(EventReadSerializer(event).data)

    @swagger_auto_schema(
        request_body=EventBaseSerializer, responses={200: EventReadSerializer}
    )
    def create(self, request: Request) -> Response:
        # we're sure this is a query dict because of the parser that
        # applies to this view
        pre_processed_data = pre_process_data(
            request.data.dict() if isinstance(request.data, QueryDict) else request.data
        )
        pre_processed_data["partner_id"] = get_request_partner_id(request)
        event = event_service.create(
            obj_data=pre_processed_data, serializer=EventSerializer
        )
        return Response(EventReadSerializer(event).data)

    @swagger_auto_schema(
        request_body=EventBaseSerializer, responses={200: EventReadSerializer}
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        pre_processed_data = pre_process_data(
            request.data.dict() if isinstance(request.data, QueryDict) else request.data
        )
        event = event_service.get(pk=pk)
        if not event:
            raise ObjectNotFoundException("Event", str(pk))
        check_self(request, str(event.partner.owner.id))
        event = event_service.update(
            obj_data=pre_processed_data,
            serializer=EventUpdateSerializer,
            obj_id=pk,
        )
        return Response(EventReadSerializer(event).data)


class TicketTypeViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerMembershipPermissions],
        "update": [PartnerMembershipPermissions],
    }
    pagination_class = CustomPagination

    @swagger_auto_schema(responses={200: TickeTypeReadSerializer(many=True)})
    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        if not filters or "event_id" not in filters:
            raise HttpErrorException(
                status_code=status.HTTP_403_FORBIDDEN,
                code=ErrorCodes.GENERIC_TICKET_TYPE_LISTING,
            )
        ticket_types = ticket_type_service.get_filtered(
            filters=filters, paginator=paginator
        )
        paginated_tickets = paginator.paginate_queryset(ticket_types, request=request)
        return paginator.get_paginated_response(
            TickeTypeReadSerializer(paginated_tickets, many=True).data
        )


class EventPromotionViewset(AbstractPermissionedView):

    permissions_by_action = {
        "create": [PartnerMembershipPermissions],
        "update": [PartnerMembershipPermissions],
        "list": [PartnerOwnerPermissions],
    }
    pagination_class = CustomPagination

    @swagger_auto_schema(
        request_body=EventPromotionSerializer,
        responses={200: EventPromotionReadSerializer},
    )
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

    @swagger_auto_schema(
        request_body=EventPromotionBaseSerializer,
        responses={200: EventPromotionReadSerializer},
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        event_promo = event_promo_service.get(pk=pk)
        if not event_promo:
            raise ObjectNotFoundException("Event Promotion", str(pk))
        check_self(request, str(event_promo.event.partner.owner.id))
        event_promo = event_promo_service.update(
            obj_data=request.data, serializer=EventPromotionUpdateSerializer, obj_id=pk
        )
        return Response(EventPromotionReadSerializer(event_promo).data)

    @swagger_auto_schema(responses={200: EventPromotionReadSerializer(many=True)})
    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        filters["event__partner__owner_id"] = get_request_user_id(request)
        event_promos = event_promo_service.get_filtered(
            filters=filters, paginator=paginator
        )
        event_promos_list = paginator.paginate_queryset(event_promos, request=request)
        return paginator.get_paginated_response(
            EventPromotionReadSerializer(event_promos_list, many=True).data
        )
