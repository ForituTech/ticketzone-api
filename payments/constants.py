from enum import Enum
from typing import List, Tuple


class PaymentStates(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"


class PaymentProviders(Enum):
    MPESA = "MPESA"
    BANK = "BANK"

    @classmethod
    def list(cls) -> List[Tuple[str, str]]:
        return [(entry.name, entry.value) for entry in cls]


class PaymentTransactionState(Enum):
    FAILED = "FAILED"
    INITIATED = "INITIATED"
    SUCCEEDED = "SUCCEEDED"


CONFIRMED_PAYMENT_STATES = [PaymentStates.PAID.value, PaymentStates.OVERPAID.value]
