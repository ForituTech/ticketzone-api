from django.contrib import admin

from .models import Payment, PaymentMethod


class PaymentAdminConfig(admin.ModelAdmin):
    search_fields = [
        "person__name",
        "person__phone_number",
        "made_through",
        "transaction_id",
    ]
    readonly_fields = [
        "verified",
        "reconciled",
        "number",
        "amount",
        "person",
        "state",
        "made_through",
        "transaction_id",
    ]


class PaymentMethodAdminConfig(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Payment, PaymentAdminConfig)
admin.site.register(PaymentMethod, PaymentMethodAdminConfig)
