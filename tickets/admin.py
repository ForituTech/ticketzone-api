from typing import Any, Sequence

from django.contrib import admin

from notifications.utils import send_ticket_email
from tickets.models import Ticket


@admin.action(description="Send Ticket(s)")
def send_tickets_manual(modeladmin: Any, r: Any, tickets: Sequence[Ticket]) -> Any:
    for ticket in tickets:
        send_ticket_email(
            ticket.id,
        )


class TicketAdminConfig(admin.ModelAdmin):
    search_fields = [
        "payment__person__name",
        "payment__person__phone_number",
        "payment__transaction_id",
        "ticket_type__event__name",
    ]
    actions = [send_tickets_manual]


admin.site.register(Ticket, TicketAdminConfig)
