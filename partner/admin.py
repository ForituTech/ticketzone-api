from django.contrib import admin

from .models import (
    Partner,
    PartnerPerson,
    PartnerPromotion,
    PartnerSMS,
    Person,
    PromoOptIn,
    TempOTPStore,
)


class PersonAdminConfig(admin.ModelAdmin):
    search_fields = ["name", "phone_number"]


class PartnerAdminConfig(admin.ModelAdmin):
    search_fields = ["name", "owner__name", "owner__phone_number"]


class PartnerSMSConfig(admin.ModelAdmin):
    search_fields = [
        "partner__name",
        "partner__owner__name",
        "partner__owner__phone_number",
    ]


class PartnerPromoConfig(admin.ModelAdmin):
    search_fields = [
        "partner__name",
        "partner__owner__name",
        "partner__owner__phone_number",
        "message",
    ]


class PartnerOptinConfig(admin.ModelAdmin):
    search_fields = [
        "partner__name",
        "partner__owner__name",
        "partner__owner__phone_number",
        "person__name",
        "person__phone_number",
    ]


class PartnerPersonConfig(admin.ModelAdmin):
    search_fields = [
        "partner__name",
        "partner__owner__name",
        "partner__owner__phone_number",
        "person__name",
        "person__phone_number",
    ]


admin.site.register(Person, PersonAdminConfig)
admin.site.register(Partner, PartnerAdminConfig)
admin.site.register(PartnerSMS, PartnerSMSConfig)
admin.site.register(PartnerPromotion, PartnerPromoConfig)
admin.site.register(PromoOptIn, PartnerOptinConfig)
admin.site.register(PartnerPerson, PartnerPersonConfig)
admin.site.register(TempOTPStore)
