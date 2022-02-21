from typing import Union

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
from core.views import AbstractPermissionedView
from partner.serializers import (
    PersonCreateSerializer,
    PersonReadSerializer,
    PersonUpdateSerializer,
)
from partner.services import person_service
from partner.utils import create_access_token, verify_password


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
    def retrieve(self, request: Request, pk: Union[str, int]) -> Response:
        person = person_service.get(pk=pk)
        if not person:
            raise HttpErrorException(
                status_code=status.HTTP_404_NOT_FOUND, code=ErrorCodes.INVALID_PERSON_ID
            )
        return Response(PersonReadSerializer(person).data)

    def create(self, request: Request) -> Response:
        person = person_service.create(
            obj_data=request.data, serializer=PersonCreateSerializer
        )
        return Response(PersonReadSerializer(person).data)

    def update(self, request: Request, pk: Union[str, int]) -> Response:
        person = person_service.update(
            obj_data=request.data, serializer=PersonUpdateSerializer, obj_id=pk
        )
        return Response(PersonReadSerializer(person).data)
