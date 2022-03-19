from typing import List

from django.db import models
from django.db.models.query import QuerySet

from core.models import BaseModel
from events.constants import EventState
from partner.models import Partner, Person
from payments.models import Payment


class EventCategory(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Event(BaseModel):
    name = models.CharField(
        max_length=256, null=False, blank=False, default="new-event"
    )
    poster = models.ImageField(null=False, blank=False, upload_to="media/")
    event_date = models.DateField(null=False, blank=False, auto_now=False)
    event_location = models.CharField(max_length=1024, null=False, blank=False)
    description = models.CharField(max_length=1024, null=False, blank=False)
    time = models.TimeField(null=False, blank=False, auto_now_add=True)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )
    category = models.ForeignKey(
        EventCategory, on_delete=models.SET_NULL, null=True, blank=True
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

    @property
    def sales(self) -> float:
        filters = {"ticket_type__event_id": self.id}
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters)
        total_sales = 0.0
        for ticket in tickets:
            total_sales += ticket.payment.amount
        return total_sales

    @property
    def redemtion_rate(self) -> float:
        filters = {
            "ticket_type__event_id": self.id,
        }
        filters_redeemed = {
            "ticket_type__event_id": self.id,
            "redeemed": True,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters)
        tickets_redeemed: QuerySet[Ticket] = Ticket.objects.filter(**filters_redeemed)
        return len(tickets_redeemed) / len(tickets)


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

    @property
    def sales(self) -> float:
        filters = {
            "ticket_type__id": self.id,
        }
        tickets: QuerySet[Ticket] = Ticket.objects.filter(**filters)
        sales = 0.0
        for ticket in tickets:
            sales += ticket.payment.amount
        return sales


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


class Ticket(BaseModel):
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="tickets",
    )
    sent = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Has the ticket been sent to the user",
    )
    redeemed = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Has the ticket been redeemed",
    )
    hash = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return (
            f"{self.payment.person.name}'s "
            f"{self.ticket_type.event.name} "
            f"{self.ticket_type.name} ticket"
        )


class ReminderOptIn(BaseModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
