from django.contrib import admin

from tickets.models import Ticket


class TicketAdminConfig(admin.ModelAdmin):
    search_fields = [
        "payment__person__name",
        "payment__person__phone_number",
        "payment__transaction_id",
        "ticket_type__event__name",
    ]


admin.site.register(Ticket, TicketAdminConfig)
