from datetime import datetime, timedelta
from typing import List

from django.db import models

from core.models import BaseModel
from events.constants import EventState
from partner.models import Partner


class Event(BaseModel):
    name = models.CharField(
        max_length=256, null=False, blank=False, default="new-event"
    )
    poster = models.ImageField(null=False, blank=False, upload_to="media/")
    event_date = models.DateField(null=False, blank=False, auto_now=False)
    event_location = models.CharField(max_length=1024, null=False, blank=False)
    description = models.CharField(max_length=1024, null=False, blank=False)
    time = models.TimeField(
        null=False,
        blank=False,
        default="{:%H:%M}".format(datetime.now() + timedelta(hours=3)),
    )
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )
    is_public = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Has the event been published",
    )
    event_state = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        default=EventState.PRE_REVIEW,
        choices=EventState.choices,
    )

    def __str__(self) -> str:
        return self.name

    @classmethod
    @property
    def search_vector(cls) -> List[str]:
        return [
            "name",
            "event_location",
            "description",
        ]


class TicketType(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    amsg = models.CharField(
        verbose_name="Active Message",
        max_length=256,
        null=False,
        blank=False,
        default="Open Soon",
    )
    amount = models.IntegerField(null=False, blank=False, default=100)
    is_visible = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Is Ticket Visible To Users",
    )

    def __str__(self) -> str:
        return "{0} - {1}".format(self.event.name, self.name)


class EventPromotion(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    promotion_rate = models.FloatField(null=False, blank=False, default=10.0)
    expiry = models.DateField(null=False, blank=False, auto_now=False)
    use_limit = models.IntegerField(null=False, blank=False, default=100)

    def __str__(self) -> str:
        return self.name


class TicketPromotion(BaseModel):
    name = models.CharField(max_length=256, null=False, blank=False)
    ticket = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
    promotion_rate = models.FloatField(null=False, blank=False, default=10.0)
    expiry = models.DateField(null=False, blank=False, auto_now=False)
    use_limit = models.IntegerField(null=False, blank=False, default=100)

    def __str__(self) -> str:
        return self.name
