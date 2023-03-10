from datetime import datetime, timedelta

from django.db import models

from core.models import BaseModel
from partner.models import Partner
from partner_api.utils import generate_resource_secret


def default_token_expiry() -> datetime:
    return datetime.today() + timedelta(hours=2)


def default_refresh_token_expiry() -> datetime:
    return datetime.today() + timedelta(hours=24)


class ApiCredentials(BaseModel):
    secret = models.CharField(max_length=255, default=generate_resource_secret)
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE)


class ApiAuthToken(BaseModel):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE)
    expiry = models.DateTimeField(default=default_token_expiry)
    refresh_expiry = models.DateTimeField(default=default_refresh_token_expiry)
