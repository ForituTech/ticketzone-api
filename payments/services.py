from core.services import CRUDService
from payments.models import Payment
from payments.serilaizers import PaymentCreateSerializer, PaymentUpdateSerializer


class PaymentService(
    CRUDService[Payment, PaymentCreateSerializer, PaymentUpdateSerializer]
):
    pass


payment_service = PaymentService(Payment)
