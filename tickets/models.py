from django.db import models

from events.models import TicketType
from partner.models import Person
from payments.models import Payment


class Ticket(models.Model):
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, null=False, blank=False
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

    def __str__(self) -> str:
        return f"{self.person.name}'s {self.ticket_type.event.name} {self.ticket_type.name} ticket"

    def send(self) -> bool:
        pass
