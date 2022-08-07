from http import HTTPStatus

from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.pagination import CustomPagination
from core.serializers import DefaultQuerySerialzier
from core.utils import _stream_model_data
from core.views import AbstractPermissionedView
from partner.permissions import (
    LoggedInPermission,
    PartnerMembershipPermissions,
    PartnerOwnerPermissions,
    TicketingAgentPermissions,
    check_self_no_partnership,
    get_request_partner_id,
    get_request_user_id,
)
from tickets.serializers import (
    TicketCreateSerializer,
    TicketReadSerializer,
    TicketSerializer,
    TotalSalesOverTime,
)
from tickets.services import ticket_service

paginator = PageNumberPagination()
paginator.page_size = 15


@swagger_auto_schema(method="get", responses={200: TotalSalesOverTime})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def ticket_sales_per_day(request: Request) -> Response:
    partner_id = get_request_partner_id(request)
    counts_set = ticket_service.counts_over_time(partner_id)
    counts = {"data": counts_set}
    return Response(TotalSalesOverTime(counts).data)  # type: ignore


@swagger_auto_schema(method="post", responses={200: TicketReadSerializer(many=True)})
@api_view(["POST"])
@permission_classes([TicketingAgentPermissions])
def redeem_ticket(request: Request, pk: str) -> Response:
    ticket = ticket_service.redeem(pk=pk)
    return Response(TicketReadSerializer(ticket).data)


@swagger_auto_schema(method="get", responses={200: TicketReadSerializer(many=True)})
@api_view(["GET"])
@permission_classes([TicketingAgentPermissions])
def read_ticket_by_hash(request: Request, hash: str) -> Response:
    filters = {
        "hash": hash,
    }
    tickets = ticket_service.get_filtered(
        paginator=paginator, request=request, filters=filters
    )
    if len(tickets) > 1:
        raise HttpErrorException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=ErrorCodes.MULTIPLE_TICKETS_ONE_HASH,
        )
    if len(tickets) == 0:
        raise HttpErrorException(
            status_code=HTTPStatus.NOT_FOUND,
            code=ErrorCodes.UNRESOLVABLE_HASH,
        )
    return Response(TicketReadSerializer(tickets[0]).data)


@swagger_auto_schema(method="get")
@api_view(["GET"])
@permission_classes([TicketingAgentPermissions])
@renderer_classes([CSVRenderer])
def export_tickets(request: Request) -> StreamingHttpResponse:
    tickets = ticket_service.get_all()
    response = StreamingHttpResponse(
        request.accepted_renderer.render(
            _stream_model_data(queryset=tickets, serializer=TicketReadSerializer)
        ),
        status=200,
        content_type="text/csv",
    )
    response["Content-Disposition"] = 'attachment; filename="tickets.csv"'
    return response


class TicketViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "create": [LoggedInPermission],
        "list": [PartnerOwnerPermissions],
        "retrieve": [TicketingAgentPermissions],
        "update": [TicketingAgentPermissions],
    }
    pagination_class = CustomPagination

    @swagger_auto_schema(
        responses={200: TicketReadSerializer(many=True)},
        query_serializer=DefaultQuerySerialzier,
    )
    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        filters["ticket_type__event__partner__owner_id"] = get_request_user_id(request)
        tickets = ticket_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        tickets_paginated = paginator.paginate_queryset(tickets, request=request)
        return paginator.get_paginated_response(
            TicketReadSerializer(tickets_paginated, many=True).data
        )

    @swagger_auto_schema(
        request_body=TicketSerializer, responses={200: TicketReadSerializer}
    )
    def create(self, request: Request) -> Response:
        ticket = ticket_service.create(
            obj_data=request.data, serializer=TicketCreateSerializer
        )
        try:
            check_self_no_partnership(
                request=request, pk=str(ticket.ticket_type.event.partner.owner_id)
            )
        except Exception as exc:
            ticket.delete()
            raise exc
        return Response(TicketReadSerializer(ticket).data)

    @swagger_auto_schema(responses={200: TicketReadSerializer})
    def retrieve(self, request: Request, pk: str) -> Response:
        ticket = ticket_service.get(pk=pk)
        if not ticket:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_TICKET_ID
            )
        return Response(TicketReadSerializer(ticket).data)
