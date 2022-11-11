import abc
from typing import Optional

from partner.models import Partner
from payments.constants import PaymentStates
from payments.models import Payment


class PaymentProviderType(abc.ABCMeta):
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
