from typing import Any

from fastapi import Depends
from fastapi.routing import APIRouter, Request

from partner.models import Partner
from partner_api import templates
from partner_api.auth.deps import current_partner
from partner_api.payments.serializers import (
    PaymentIntentCreateSerializer,
    PaymentIntentSerializer,
)
from partner_api.payments.services import payments_service

router = APIRouter()


@router.post("/intent/", response_model=PaymentIntentSerializer)
def create_payment_intent(
    *,
    payment_in: PaymentIntentCreateSerializer,
    _: Partner = Depends(current_partner),
) -> Any:
    return payments_service.create_payment_intent(payment_in=payment_in)


@router.get("/{intent_id}/", include_in_schema=False)
def ipn_page(*, intent_id: str, request: Request) -> Any:
    intent = payments_service.get_payment_intent(intent_id)
    event = payments_service.get_related_event(intent_id)
    return templates.TemplateResponse(
        "index.html", context={"request": request, "intent": intent, "event": event}
    )
