from django.db import models

from core.models import BaseModel
from partner.constants import PersonType


class Person(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    email = models.CharField(
        verbose_name="E-mail", max_length=256, null=False, blank=False, default="0"
    )
    phone_number = models.CharField(max_length=15, null=False, blank=False, unique=True)
    hashed_password = models.CharField(max_length=1024, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class PartnerBankingInfo(BaseModel):
    bank_code = models.IntegerField(null=False, blank=False)
    bank_account_number = models.BigIntegerField(null=False, blank=False)


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
    banking_info = models.ForeignKey(
        PartnerBankingInfo, on_delete=models.CASCADE, null=False, blank=False
    )
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
