from datetime import datetime

from jwt import DecodeError

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorExceptionFA as HttpErrorException
from partner_api.auth.serializers import LoginCredentialsSerializer
from partner_api.auth.utils import (
    TokenResponse,
    create_auth_token,
    decode_token,
    get_auth_signature,
)
from partner_api.models import ApiCredentials


class AuthService:
    def get_auth_tokens(
        self, *, credentials: LoginCredentialsSerializer
    ) -> TokenResponse:
        api_creds = ApiCredentials.objects.filter(id=credentials.partner_key).first()
        if not api_creds:
            raise HttpErrorException(status_code=400, code=ErrorCodes.PARTNER_NOT_FOUND)

        expected_signature = get_auth_signature(
            api_creds=api_creds, credentials=credentials
        )
        if credentials.signature != expected_signature:
            raise HttpErrorException(status_code=400, code=ErrorCodes.INVALID_SIGNATURE)

        return create_auth_token(api_creds=api_creds)

    def refresh_token(self, *, refresh_token: str) -> TokenResponse:
        try:
            details = decode_token(refresh_token)
        except DecodeError:
            raise HttpErrorException(
                status_code=400, code=ErrorCodes.INVALID_REFRESH_TOKEN
            )
        expiry = datetime.fromisoformat(details["expires"])
        if expiry < datetime.now():
            raise HttpErrorException(
                status_code=401, code=ErrorCodes.EXPIRED_REFRESH_TOKEN
            )

        api_creds = ApiCredentials.objects.filter(id=details["access_key"]).first()
        if not api_creds:
            raise HttpErrorException(status_code=400, code=ErrorCodes.PARTNER_NOT_FOUND)

        return create_auth_token(api_creds=api_creds)


auth_service = AuthService()
