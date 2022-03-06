from http import HTTPStatus
from typing import Union

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.views import AbstractPermissionedView
from partner.permissions import PartnerOwnerPermissions, check_self
from partner.serializers import (
    PartnerBaseSerializer,
    PartnerPersonBaseSerializer,
    PartnerPersonCreateSerializer,
    PartnerPersonReadSerializer,
    PartnerPersonUpdateSerializer,
    PartnerReadSerializer,
    PartnerUpdateSerializer,
    PersonBaseSerializer,
    PersonCreateSerializer,
    PersonReadSerializer,
    PersonSerializer,
    PersonUpdateSerializer,
    TokenSerializer,
)
from partner.services import partner_person_service, partner_service, person_service
from partner.utils import create_access_token, create_access_token_lite, verify_password


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
