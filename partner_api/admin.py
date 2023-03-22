from django.contrib import admin

from partner_api.models import PaymentIntent


class PaymentIntentAdmin(admin.ModelAdmin):
    pass


admin.site.register(PaymentIntent, PaymentIntentAdmin)
