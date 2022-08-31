from typing import List

from django.db import models
from django.db.models.query import QuerySet

from core.models import BaseModel
from core.utils import generate_event_number, generate_ticket_number
from events.constants import EventState
from partner.models import Partner, PartnerPerson, Person
from payments.models import Payment


class EventCategory(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Event(BaseModel):
    event_number = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        default=generate_event_number,
    )
    name = models.CharField(
        max_length=256, null=False, blank=False, default="new-event"
    )
    poster = models.ImageField(null=False, blank=False, upload_to="media/")
    event_date = models.DateField(null=False, blank=False, auto_now=False)
    time = models.TimeField(null=False, blank=False, auto_now_add=True)
    event_end_date = models.DateField(null=False, blank=False, auto_now=False)
    end_time = models.TimeField(null=False, blank=False, auto_now_add=True)
    event_location = models.CharField(max_length=1024, null=False, blank=False)
    description = models.CharField(max_length=1024, null=False, blank=False)
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

    _assigned_ticketing_agents = models.ManyToManyField(
        PartnerPerson, through="PartnerPersonSchedule"
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
            "partner__name",
            "event_number",
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
    def redemption_rate(self) -> float:
        filters = {
            "ticket_type__event_id": self.id,
        }
        filters_redeemed = {
            "ticket_type__event_id": self.id,
            "redeemed": True,
        }
        tickets = Ticket.objects.filter(**filters).count()
        tickets_redeemed = Ticket.objects.filter(**filters_redeemed).count()
        try:
            return (tickets_redeemed / tickets) * 100
        except ZeroDivisionError:
            return 0

    @property
    def tickets_sold(self) -> int:
        filters = {"ticket_type__event_id": self.id}
        return Ticket.objects.filter(**filters).count()

    @property
    def assigned_ticketing_agents(self) -> QuerySet[PartnerPerson]:
        return self._assigned_ticketing_agents.all()

    @property
    def ticket_types(self) -> QuerySet["TicketType"]:
        return self.tickettype_set.all()


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
    use_limit = models.IntegerField(null=False, blank=False, default=1)

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
    ticket_number = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        default=generate_ticket_number,
    )
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
    uses = models.IntegerField(null=False, blank=False, default=0)
    hash = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return (
            f"{self.payment.person.name}'s "
            f"{self.ticket_type.event.name} "
            f"{self.ticket_type.name} ticket"
        )

    @classmethod
    @property
    def search_vector(cls) -> List[str]:
        return [
            "hash",
            "ticket_number",
            "payment__person__name",
            "payment__person__email",
            "payment__person__phone_number",
            "ticket_type__name",
            "ticket_type__event__name",
        ]


class ReminderOptIn(BaseModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.person.name}'s reminder for {self.event.name}"


class PartnerPersonSchedule(BaseModel):
    partner_person = models.OneToOneField(
        PartnerPerson, on_delete=models.CASCADE, null=False, blank=False
    )
    event = models.ForeignKey(Event, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.partner_person.person.name} is scheduled as TA for {self.event.name}"
