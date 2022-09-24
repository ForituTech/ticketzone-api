from enum import Enum


class PaymentStates(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"


class PaymentProviders(Enum):
    MPESA = "MPESA"
    BANK = "BANK"
