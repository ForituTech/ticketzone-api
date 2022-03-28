from datetime import date, timedelta
from typing import Any, Optional

from django.db import models

from core.models import BaseModel
from partner.constants import PartnerPromotionPeriod, PersonType


class Person(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    email = models.CharField(
        verbose_name="E-mail", max_length=256, null=False, blank=False, default="0"
    )
    phone_number = models.CharField(max_length=15, null=False, blank=False, unique=True)
    hashed_password = models.CharField(max_length=1024, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Partner(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    owner = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="owner",
    )
    contact_person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True
    )
    bank_code = models.CharField(null=False, blank=False, max_length=255)
    bank_account_number = models.CharField(null=False, blank=False, max_length=512)
    comission_rate = models.FloatField(null=False, blank=False, default=3.0)

    def __str__(self) -> str:
        return self.name


class PartnerPerson(BaseModel):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    person_type = models.CharField(
        max_length=255,
        choices=PersonType.choices,
        null=False,
        blank=False,
        default=PersonType.CUSTOMER,
    )
    is_active = models.BooleanField(
        verbose_name="Is the member active", null=False, blank=False, default=True
    )
    is_hidden = models.BooleanField(
        verbose_name="Is the person hidden", null=False, blank=False, default=False
    )

    def __str__(self) -> str:
        return f"{self.person.name}: [{self.partner.name} {self.person_type}]"


class PartnerSMS(BaseModel):
    partner = models.OneToOneField(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )
    per_sms_rate = models.FloatField(
        "Partner Cost Per SMS", null=False, blank=False, default=0.0
    )
    sms_limit = models.IntegerField(null=False, blank=False, default=0)
    sms_used = models.IntegerField(null=False, blank=False, default=0)
    verified = models.BooleanField(null=False, blank=False, default=False)

    @property
    def sms_left(self) -> bool:
        return (self.sms_limit - self.sms_used) > 0 and self.verified

    def __str__(self) -> str:
        return f"{self.partner.name} SMS package"


class PartnerPromotion(BaseModel):
    name = models.CharField(max_length=1024, null=False, blank=False)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )
    repeat = models.CharField(
        max_length=255,
        choices=PartnerPromotionPeriod.choices,
        null=False,
        blank=False,
        default=PartnerPromotionPeriod.FIXED,
    )
    message = models.TextField(null=False, blank=False, max_length=10240)
    # channel = models.CharField()
    starts_on = models.DateField(null=False, blank=False, auto_now_add=True)
    last_run = models.DateField(null=False, blank=False, auto_now_add=True)
    stops_on = models.DateField(null=False, blank=False, auto_now_add=True)
    verified = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self) -> str:
        return f"{self.partner.name}'s {self.name} promotion"

    @property
    def next_run(self) -> Optional[Any]:
        if date.today() > self.stops_on:
            return None
        if self.repeat == PartnerPromotionPeriod.WEEKLY:
            return self.last_run + timedelta(weeks=1)
        if self.repeat == PartnerPromotionPeriod.MONTHLY:
            return self.last_run + timedelta(days=30)
        if self.repeat == PartnerPromotionPeriod.FIXED:
            return self.starts_on
        return None


class PromoOptIn(BaseModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False
    )
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )

    def __str__(self) -> str:
        return f"{self.person.name}'s promo opt in for {self.partner.name}'s events"
