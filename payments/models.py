import abc
from typing import Optional

from django.db import models

from core.models import BaseModel
from partner.models import Partner, Person
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


class AbstractModelMeta(abc.ABCMeta, type(models.Model)):  # type: ignore
    pass


class PaymentMethodType(models.Model, metaclass=AbstractModelMeta):  # type: ignore

    name = models.CharField(max_length=256, null=False, blank=False, unique=True)

    class Meta:
        abstract = True

    @abc.abstractmethod
    def verify(self) -> bool:
        pass

    @abc.abstractmethod
    def c2b_receive(self, *, amount: int) -> PaymentStates:
        pass

    @abc.abstractmethod
    def b2c_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    # partner disbursment
    @abc.abstractmethod
    def b2b_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    @abc.abstractmethod
    def search(self, *, transaction_id: str) -> Optional[Payment]:
        pass
