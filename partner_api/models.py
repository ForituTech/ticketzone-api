from datetime import datetime, timedelta
from typing import Optional, Sequence

from django.db import models

from core.models import BaseModel
from eticketing_api.settings import PAYMENT_PAGE_URL
from events.models import TicketType
from partner.models import Partner, Person
from partner_api.utils import generate_resource_secret


def default_token_expiry() -> datetime:
    return datetime.today() + timedelta(hours=2)


def default_refresh_token_expiry() -> datetime:
    return datetime.today() + timedelta(hours=24)


class ApiCredentials(BaseModel):
    secret = models.CharField(max_length=255, default=generate_resource_secret)
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE)


class ApiAuthToken(BaseModel):
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE)
    expiry = models.DateTimeField(default=default_token_expiry)
    refresh_expiry = models.DateTimeField(default=default_refresh_token_expiry)


# Pivot model for payment intents and ticket types
# given there can be a many to one relationship
# between the 2
class PaymentIntentTicketType(BaseModel):
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
    payment_intent = models.ForeignKey(
        "PaymentIntent", on_delete=models.CASCADE, null=False, blank=False
    )
    amount = models.IntegerField(default=0, null=False, blank=False)


class PaymentIntent(BaseModel):
    amount = models.FloatField(null=False, blank=False)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False
    )
    ticket_type_rel = models.ManyToManyField(
        TicketType, through=PaymentIntentTicketType
    )
    callback_url = models.URLField(null=False, blank=False)

    @property
    def ticket_types(self) -> Sequence[TicketType]:
        ticket_types = [ticket_type for ticket_type in self.ticket_type_rel.all()]
        for tt in ticket_types:
            amount = (
                PaymentIntentTicketType.objects.values("amount")
                .filter(ticket_type_id=tt.id, payment_intent_id=self.id)
                .first()
            )
            setattr(tt, "amount", amount["amount"] if amount else 0)

        return ticket_types

    @property
    def redirect_to(self) -> str:
        return "".join([PAYMENT_PAGE_URL, "/", str(self.id)])

    @property
    def event_poster(self) -> Optional[str]:
        if self.ticket_types:
            return self.ticket_types[0].event.poster

        return None
