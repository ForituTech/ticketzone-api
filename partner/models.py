from django.contrib.auth.models import User
from django.db import models

from core.db import BaseModel


class Person(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    email = models.CharField(
        verbose_name="E-mail", max_length=256, null=False, blank=False, default="0"
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class PartnerBankingInfo(BaseModel):
    bank_code = models.IntegerField(null=False, blank=False)
    bank_account_number = models.IntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f"Banking info"


class Partner(BaseModel):
    owner = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False, related_name="owner"
    )
    contact_person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True
    )
    banking_info = models.ForeignKey(
        PartnerBankingInfo, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.owner.name
