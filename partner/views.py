from http import HTTPStatus
from typing import Union

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.serializers import VerifyActionSerializer
from core.views import AbstractPermissionedView
from events.serializers import EventWithSales, TicketTypeWithSales
from events.services import ticket_type_service
from partner.permissions import (
    LoggedInPermission,
    PartnerMembershipPermissions,
    PartnerOwnerPermissions,
    check_self,
    get_request_partner_id,
)
from partner.serializers import (
    PartnerBaseSerializer,
    PartnerPersonBaseSerializer,
    PartnerPersonCreateSerializer,
    PartnerPersonReadSerializer,
    PartnerPersonUpdateSerializer,
    PartnerPromoBaseSerializer,
    PartnerPromoCreateSerializer,
    PartnerPromoReadSerializer,
    PartnerPromoSerializer,
    PartnerPromoUpdateSerializer,
    PartnerReadSerializer,
    PartnerSMSPackageCreateSerializer,
    PartnerSMSPackageReadSerializer,
    PartnerUpdateSerializer,
    PersonBaseSerializer,
    PersonCreateSerializer,
    PersonReadSerializer,
    PersonSerializer,
    PersonUpdateSerializer,
    RedemtionRateSerializer,
    SalesSerializer,
    TokenSerializer,
)
from partner.services import (
    partner_person_service,
    partner_promo_service,
    partner_service,
    partner_sms_service,
    person_service,
)
from partner.utils import (
    create_access_token,
    create_access_token_lite,
    get_user_from_access_token,
    verify_password,
)

paginator = PageNumberPagination()
paginator.page_size = 15


@swagger_auto_schema(method="post", responses={200: TokenSerializer})
@api_view(["POST"])
def login(request: Request) -> Response:
    token_key = "Authorization"
    if token_key in request.META:
        return Response(data="Already logged in", status=status.HTTP_202_ACCEPTED)
    user_group = person_service.get_by_phonenumber(request)
    if verify_password(
        str(user_group[1].data["password"]), user_group[0].hashed_password
    ):
        request.session[token_key] = create_access_token(user_group[0])
        data = {
            "token": request.session[token_key],
        }
        return Response(
            data, status=status.HTTP_200_OK, content_type="application/json"
        )
    else:
        raise HttpErrorException(status_code=404, code=ErrorCodes.INVALID_CREDENTIALS)


@swagger_auto_schema(method="get", responses={200: SalesSerializer})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def partner_sales(request: Request) -> Response:
    partner_id = get_request_partner_id(request)
    sales = partner_service.get_total_sales(partner_id)
    sales_dict = {"sales": sales}
    return Response(SalesSerializer(sales_dict).data)


@swagger_auto_schema(method="get", responses={200: RedemtionRateSerializer})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def partner_redemtion_rate(request: Request) -> Response:
    partner_id = get_request_partner_id(request)
    rate = partner_service.get_total_redemtion_rate(partner_id)
    rate_dict = {"rate": rate}
    return Response(RedemtionRateSerializer(rate_dict).data)


@swagger_auto_schema(method="get", responses={200: EventWithSales(many=True)})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def partner_ranked_events(request: Request) -> Response:
    partner_id = get_request_partner_id(request)
    events = partner_service.get_ranked_events_by_sales(partner_id)
    return Response(EventWithSales(events, many=True).data)


@swagger_auto_schema(method="get", responses={200: TicketTypeWithSales(many=True)})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def partner_event_ticket_with_sales(request: Request, event_id: str) -> Response:
    filters = {"event_id": event_id}
    ticket_types = ticket_type_service.get_filtered(
        paginator=paginator, request=request, filters=filters
    )
    return Response(TicketTypeWithSales(ticket_types, many=True).data)


@swagger_auto_schema(method="post", responses={200: VerifyActionSerializer()})
@api_view(["POST"])
@permission_classes([LoggedInPermission])
def partner_promo_optin(request: Request, partner_id: str) -> Response:
    token_key = "Authorization"
    person_id = get_user_from_access_token(request.META[token_key]).id
    partner_service.add_promo_opt_in(partner_id, str(person_id))
    return Response({"done": True})


@swagger_auto_schema(method="get", responses={200: VerifyActionSerializer()})
@api_view(["GET"])
@permission_classes([PartnerMembershipPermissions])
def partner_promo_optin_count(request: Request, partner_id: str) -> Response:
    count = partner_service.promo_optin_count(partner_id)
    return Response({"count": count})


class PersonViewSet(AbstractPermissionedView):
    @swagger_auto_schema(responses={200: PersonReadSerializer})
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        check_self(request=request, pk=pk)
        person = person_service.get(pk=pk)
        if not person:
            raise HttpErrorException(
                status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_PERSON_ID
            )
        return Response(PersonReadSerializer(person).data)

    @swagger_auto_schema(
        request_body=PersonSerializer, responses={200: PersonReadSerializer}
    )
    def create(self, request: Request) -> Response:
        token_key = "Authorization"
        person = person_service.create(
            obj_data=request.data, serializer=PersonCreateSerializer
        )
        request.session[token_key] = create_access_token_lite(person)
        auth_header = {token_key: request.session[token_key]}
        return Response(PersonReadSerializer(person).data, headers=auth_header)

    @swagger_auto_schema(
        request_body=PersonBaseSerializer, responses={200: PersonReadSerializer}
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        check_self(request=request, pk=pk)
        person = person_service.update(
            obj_data=request.data, serializer=PersonUpdateSerializer, obj_id=pk
        )
        return Response(PersonReadSerializer(person).data)


class PartnerViewSet(AbstractPermissionedView):

    permissions_by_action = {
        "retrieve": [PartnerOwnerPermissions],
        "update": [PartnerOwnerPermissions],
    }

    @swagger_auto_schema(responses={200: PartnerReadSerializer})
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        partner = partner_service.get(pk=pk)
        if not partner:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_PARTNER_ID
            )
        check_self(request=request, pk=str(partner.owner.id))
        return Response(PartnerReadSerializer(partner).data)

    @swagger_auto_schema(
        request_body=PartnerBaseSerializer, responses={200: PartnerReadSerializer}
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        partner = partner_service.get(pk=pk)
        if not partner:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.INVALID_PARTNER_ID
            )
        check_self(request=request, pk=str(partner.owner.id))
        partner = partner_service.update(
            obj_data=request.data, serializer=PartnerUpdateSerializer, obj_id=pk
        )
        return Response(PartnerReadSerializer(partner).data)


class PartnerPersonViewset(AbstractPermissionedView):

    permissions_by_action = {
        "retrieve": [PartnerOwnerPermissions],
        "create": [PartnerOwnerPermissions],
        "update": [PartnerOwnerPermissions],
    }

    @swagger_auto_schema(responses={200: PartnerPersonReadSerializer})
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        return Response(
            PartnerPersonReadSerializer(partner_person_service.get(pk=pk)).data
        )

    @swagger_auto_schema(
        request_body=PartnerPersonBaseSerializer,
        responses={200: PartnerPersonReadSerializer},
    )
    def create(self, request: Request) -> Response:
        partner_person = partner_person_service.create(
            obj_data=request.data, serializer=PartnerPersonCreateSerializer
        )
        return Response(PartnerPersonReadSerializer(partner_person).data)

    @swagger_auto_schema(
        request_body=PartnerPersonBaseSerializer,
        responses={200: PartnerPersonReadSerializer},
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        partner_person = partner_person_service.update(
            obj_data=request.data, serializer=PartnerPersonUpdateSerializer, obj_id=pk
        )
        return Response(PartnerPersonReadSerializer(partner_person).data)


class PartnerSMSPackageViewset(AbstractPermissionedView):

    permissions_by_action = {
        "retrieve": [PartnerMembershipPermissions],
        "create": [PartnerMembershipPermissions],
    }

    @swagger_auto_schema(
        responses={200: PartnerSMSPackageReadSerializer},
    )
    def create(self, request: Request) -> Response:
        data = {"partner_id": get_request_partner_id(request)}
        partner_sms = partner_sms_service.create(
            obj_data=data, serializer=PartnerSMSPackageCreateSerializer
        )
        return Response(PartnerSMSPackageReadSerializer(partner_sms).data)

    @swagger_auto_schema(responses={200: PartnerSMSPackageReadSerializer})
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        partner_id = get_request_partner_id(request)
        partner_sms = partner_sms_service.get(pk=pk, partner_id=partner_id)
        return Response(PartnerSMSPackageReadSerializer(partner_sms).data)


class PartnerPromotionViewset(AbstractPermissionedView):

    permissions_by_action = {
        "retrieve": [PartnerMembershipPermissions],
        "create": [PartnerMembershipPermissions],
        "list": [PartnerMembershipPermissions],
        "update": [PartnerMembershipPermissions],
    }

    @swagger_auto_schema(
        responses={200: PartnerPromoReadSerializer},
    )
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        partner_id = get_request_partner_id(request)
        partner_promo = partner_promo_service.get(pk=pk, partner_id=partner_id)
        if not partner_promo:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.PROMO_NOT_FOUND
            )
        return Response(PartnerPromoReadSerializer(partner_promo).data)

    @swagger_auto_schema(
        request_body=PartnerPromoSerializer,
        responses={200: PartnerPromoReadSerializer},
    )
    def create(self, request: Request) -> Response:
        request.data["partner_id"] = get_request_partner_id(request)
        partner_promo = partner_promo_service.create(
            obj_data=request.data, serializer=PartnerPromoCreateSerializer
        )
        return Response(PartnerPromoReadSerializer(partner_promo).data)

    @swagger_auto_schema(
        responses={200: PartnerPromoReadSerializer(many=True)},
    )
    def list(self, request: Request) -> Response:
        filters = request.query_params.dict()
        filters.update(
            {
                "partner_id": get_request_partner_id(request),
            }
        )
        promos = partner_promo_service.get_filtered(
            paginator=paginator, request=request, filters=filters
        )
        paginated_promos = paginator.paginate_queryset(promos, request)
        return paginator.get_paginated_response(
            PartnerPromoReadSerializer(paginated_promos, many=True).data
        )

    @swagger_auto_schema(
        request_body=PartnerPromoBaseSerializer,
        responses={200: PartnerPromoReadSerializer},
    )
    def update(self, request: Request, pk: Union[str, int]) -> Response:
        partner_id = get_request_partner_id(request)
        mapping = {"partner_id": partner_id}
        promo = partner_promo_service.get(pk=pk, **mapping)
        if not promo:
            raise HttpErrorException(
                status_code=HTTPStatus.NOT_FOUND, code=ErrorCodes.PROMO_NOT_FOUND
            )
        promo = partner_promo_service.update(
            obj_data=request.data, serializer=PartnerPromoUpdateSerializer, obj_id=pk
        )
        return Response(PartnerPromoReadSerializer(promo).data)
