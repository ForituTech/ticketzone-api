from typing import Sequence

from fastapi_pagination.ext.django import paginate

from core.error_codes import ErrorCodes
from core.exceptions import HttpErrorExceptionFA as HttpErrorException
from events.models import Event
from partner.models import Partner
from partner_api.serializers import PaginationQueryParams


class EventsService:
    def get_events(
        self, partner: Partner, pagination_params: PaginationQueryParams
    ) -> Sequence[Event]:
        return paginate(
            Event.objects.filter(partner_id=partner.id), params=pagination_params
        )

    def read_event(self, *, event_id: str, partner: Partner) -> Event:
        event = Event.objects.filter(id=event_id, partner_id=partner.id).first()
        if not event:
            raise HttpErrorException(status_code=404, code=ErrorCodes.INVALID_EVENT_ID)

        return event


event_service = EventsService()
