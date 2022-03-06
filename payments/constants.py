from enum import Enum


class PaymentStates(Enum):
    PENDIGN = "PENDIGN"
    PAID = "PAID"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"


class PaymentProviders(Enum):
    MPESA = "MPESA"
    BANK = "BANK"
