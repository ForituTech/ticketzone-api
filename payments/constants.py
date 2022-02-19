from enum import Enum


class PaymentStates(Enum):
    PENDIGN = "PENDIGN"
    PAID = "PAID"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"
