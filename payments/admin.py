from django.contrib import admin

from .models import B2BTransactionLogs, Payment, PaymentMethod, PaymentTransactionLogs


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


class B2BLogsAdminConfig(admin.ModelAdmin):
    search_fields = [
        "partner__name" "partner__owner__name",
        "partner__owner__phone_number",
    ]
    list_filter = ("state",)


class PaymentLogsAdminConfig(admin.ModelAdmin):
    search_fields = [
        "payment__person__name",
        "payment__person__phone_number",
        "payment__made_through",
        "payment__transaction_id",
        "message",
    ]
    list_filter = ("state",)


admin.site.register(Payment, PaymentAdminConfig)
admin.site.register(PaymentMethod, PaymentMethodAdminConfig)
admin.site.register(PaymentTransactionLogs, PaymentLogsAdminConfig)
admin.site.register(B2BTransactionLogs, B2BLogsAdminConfig)
