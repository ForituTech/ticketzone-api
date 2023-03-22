from django.contrib import admin

from partner_api.models import PaymentIntent, PaymentIntentTicketType


class PaymentIntentAdmin(admin.ModelAdmin):
    pass


admin.site.register(PaymentIntent, PaymentIntentAdmin)
admin.site.register(PaymentIntentTicketType, PaymentIntentAdmin)
