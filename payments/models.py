from django.db import models

from core.models import BaseModel
from partner.models import Person
from payments.constants import PaymentProviders, PaymentStates


class Payment(BaseModel):
    amount = models.FloatField(null=False, blank=False)
    person = models.ForeignKey(
        Person, on_delete=models.DO_NOTHING, null=False, blank=False
    )
    made_through = models.CharField(
        max_length=255, null=False, blank=False, default=PaymentProviders.MPESA.value
    )
    # mapping from payment provider ids to internal relations
    transaction_id = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(
        max_length=255, null=False, blank=False, default=PaymentStates.PENDING.value
    )
    verified = models.BooleanField(null=False, blank=False, default=False)
    reconciled = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self) -> str:
        return f"{self.person.name} paid " f"{self.amount} at {self.created_at}"


class PaymentMethod(BaseModel):
    name = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        default=PaymentProviders.MPESA.value,
        choices=PaymentProviders.list(),
        unique=True,
    )
    poster = models.ImageField(null=True, blank=True, upload_to="media/")

    def __str__(self) -> str:
        return self.name
