import hashlib
import hmac
from typing import TypedDict

import jwt

from eticketing_api import settings
from partner_api.auth.serializers import LoginCredentialsSerializer
from partner_api.models import ApiAuthToken, ApiCredentials

ALGORITHM = "HS256"


class TokenResponse(TypedDict):
    access_token: str
    refresh_token: str


def create_token(
    api_creds: ApiCredentials, token: ApiAuthToken, refresh: bool = False
) -> str:
    to_encode = {
        "partner_id": str(api_creds.partner.id),
        "access_key": str(api_creds.id),
        "expires": str(token.refresh_expiry if refresh else token.expiry),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def get_auth_signature(
    *, api_creds: ApiCredentials, credentials: LoginCredentialsSerializer
) -> str:
    values_str = f"{credentials.partner_key}{credentials.now}"
    hash_obj = hmac.new(
        key=api_creds.secret.encode(), msg=values_str.encode(), digestmod=hashlib.sha256
    )
    return hash_obj.hexdigest()


def create_auth_token(*, api_creds: ApiCredentials) -> TokenResponse:
    token_obj = ApiAuthToken.objects.filter(partner_id=api_creds.partner.id).first()
    if token_obj:
        token_obj.delete()

    token_obj = ApiAuthToken(partner=api_creds.partner)
    return {
        "access_token": create_token(api_creds=api_creds, token=token_obj),
        "refresh_token": create_token(
            api_creds=api_creds, token=token_obj, refresh=True
        ),
    }
