import abc
import uuid

from django.db import models

from partner.models import Partner, Person


class AbstractModelMeta(abc.ABCMeta, type(models.Model)):
    pass


class PaymentMethodType(models.Model, metaclass=AbstractModelMeta):

    name = models.CharField(max_length=256, null=False, blank=False, unique=True)

    class Meta:
        abstract = True

    @abc.abstractmethod
    def verify(self):
        pass

    @abc.abstractmethod
    def c2b_receive(self, *, amount: int):
        pass

    @abc.abstractmethod
    def b2c_send(self, *, amount: int, partner: Partner):
        pass

    # partner disbursment
    @abc.abstractmethod
    def b2b_send(self):
        pass

    @abc.abstractmethod
    def search(self, *, transaction_id: str):
        pass


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    made_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    amount = models.IntegerField(null=False, blank=False)
    person = models.ForeignKey(
        Person, on_delete=models.DO_NOTHING, null=False, blank=False
    )
    # mapping from payment provider ids to internal relations
    transaction_id = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.person.name} paid {self.amount} at {self.made_at}"
