from typing import Any

from fastapi import Depends
from fastapi.routing import APIRouter

from partner.models import Partner
from partner_api.auth.deps import current_partner
from partner_api.events.serializers import EventSerializer
from partner_api.events.services import event_service
from partner_api.serializers import Page, PaginationQueryParams

router = APIRouter()


@router.get("/", response_model=Page[EventSerializer])
def list_events(
    params: PaginationQueryParams = Depends(),
    partner: Partner = Depends(current_partner),
) -> Any:
    return event_service.get_events(partner=partner, pagination_params=params)


@router.get("/{event_id}/", response_model=EventSerializer)
def read_event(event_id: str, partner: Partner = Depends(current_partner)) -> Any:
    return event_service.read_event(event_id=event_id, partner=partner)
