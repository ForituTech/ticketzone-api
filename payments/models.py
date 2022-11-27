from django.db import models

from core.models import BaseModel
from core.utils import generate_payment_number
from partner.models import Person
from payments.constants import PaymentProviders, PaymentStates, PaymentTransactionState


class Payment(BaseModel):
    amount = models.FloatField(null=False, blank=False)
    number = models.CharField(
        null=False,
        blank=False,
        default=generate_payment_number,
        unique=True,
        max_length=255,
    )
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


class PaymentTransactionLogs(BaseModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        default=PaymentTransactionState.FAILED.value,
    )
    message = models.CharField(max_length=2048, null=False, blank=False)
