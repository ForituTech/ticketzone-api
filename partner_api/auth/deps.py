from fastapi import Header
from jwt import DecodeError

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorExceptionFA as HttpErrorException
from partner.models import Partner
from partner_api.auth.utils import decode_token


def current_partner(*, access_token: str = Header(...)) -> Partner:
    try:
        token_details = decode_token(access_token)
    except DecodeError:
        raise HttpErrorException(status_code=400, code=ErrorCodes.INVALID_ACCESS_TOKEN)

    partner = Partner.objects.filter(id=token_details["partner_id"]).first()
    if not partner:
        raise HttpErrorException(status_code=400, code=ErrorCodes.PARTNER_NOT_FOUND)

    return partner
