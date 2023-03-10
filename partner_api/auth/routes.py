from typing import Any

from fastapi import Header
from fastapi.routing import APIRouter

from partner_api.auth.serializers import (
    LoginCredentialsSerializer,
    LoginResponseSerializer,
)
from partner_api.auth.services import auth_service

router = APIRouter()


@router.post("/", response_model=LoginResponseSerializer)
def get_auth_token(*, credentials_in: LoginCredentialsSerializer) -> Any:
    return auth_service.get_auth_tokens(credentials=credentials_in)


@router.post("/refresh/", response_model=LoginResponseSerializer)
def refresh_auth_token(*, refresh_token: str = Header(...)) -> Any:
    return auth_service.refresh_token(refresh_token=refresh_token)
