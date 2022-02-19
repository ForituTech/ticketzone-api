import abc
from typing import Optional

from django.db import models

from core.db import BaseModel
from partner.models import Partner, Person
from payments.constants import PaymentStates


class Payment(BaseModel):
    made_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    amount = models.IntegerField(null=False, blank=False)
    person = models.ForeignKey(
        Person, on_delete=models.DO_NOTHING, null=False, blank=False
    )  # type: ignore
    # mapping from payment provider ids to internal relations
    transaction_id = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self) -> str:
        return (
            f"{self.person.name} paid "  # type: ignore
            f"{self.amount} at {self.made_at}"
        )


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
