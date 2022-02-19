from django.db import models

from core.db import BaseModel
from events.models import TicketType
from payments.models import Payment


class Ticket(BaseModel):
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
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
        return (
            f"{self.payment.person.name}'s"
            f"{self.ticket_type.event.name}"
            f"{self.ticket_type.name} ticket"
        )

    def send(self) -> bool:
        pass
