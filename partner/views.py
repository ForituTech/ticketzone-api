from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorException
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
