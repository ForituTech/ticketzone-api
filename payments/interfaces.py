from abc import ABC, abstractmethod
from typing import Optional

from partner.models import Partner
from payments.constants import PaymentStates
from payments.models import Payment


class PaymentProviderType(ABC):
    @abstractmethod
    def verify(self) -> bool:
        pass

    @abstractmethod
    def c2b_receive(self, *, payment: Payment) -> None:
        # return none becuase majority of payment providers
        # use async [callback URLs]
        pass

    @abstractmethod
    def b2c_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    # partner disbursment
    @abstractmethod
    def b2b_send(self, *, amount: int, partner: Partner) -> PaymentStates:
        pass

    @abstractmethod
    def search(self, *, transaction_id: str) -> Optional[Payment]:
        pass
