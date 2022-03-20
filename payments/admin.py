from django.contrib import admin

from .models import Payment


class PaymentAdminConfig(admin.ModelAdmin):
    search_fields = [
        "person__name",
        "person__phone_number",
        "made_through",
        "transaction_id",
    ]
    readonly_fields = ["verified", "reconciled"]


admin.site.register(Payment, PaymentAdminConfig)
