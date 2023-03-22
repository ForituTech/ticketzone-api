from typing import Any

from fastapi import Depends
from fastapi.routing import APIRouter

from partner.models import Partner
from partner_api.auth.deps import current_partner
from partner_api.payments.serializers import (
    PaymentCreateSerializer,
    PaymentIntentCreateSerializer,
    PaymentIntentSerializer,
    PaymentSerializer,
)
from partner_api.payments.services import payments_service

router = APIRouter()


@router.post("/", response_model=PaymentSerializer)
def create_payment_from_intent(*, payment_in: PaymentCreateSerializer) -> Any:
    return payments_service.create_payment_from_intent(payment_in)


@router.post("/intent/", response_model=PaymentIntentSerializer)
def create_payment_intent(
    *,
    payment_in: PaymentIntentCreateSerializer,
    _: Partner = Depends(current_partner),
) -> Any:
    return payments_service.create_payment_intent(payment_in=payment_in)
