import uuid

from django.db import models

from events.models import TicketType
from payments.models import Payment


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

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
        return f"{self.payment.person.name}'s {self.ticket_type.event.name} {self.ticket_type.name} ticket"

    def send(self) -> bool:
        pass
