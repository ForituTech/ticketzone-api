from django.contrib import admin

from .models import (
    Event,
    EventCategory,
    EventPromotion,
    ReminderOptIn,
    TicketPromotion,
    TicketType,
)


class EventAdminConfig(admin.ModelAdmin):
    search_fields = [
        "name",
        "description",
        "partner__name",
        "partner__owner__name",
        "partner__owner__phone",
    ]


class EventCategoryAdminConfig(admin.ModelAdmin):
    search_fields = ["name"]


class EventPromotionAdminConfig(admin.ModelAdmin):
    search_fields = ["name", "event__name", "event__partner__name"]


class TicketPromotionAdminConfig(admin.ModelAdmin):
    search_fields = [
        "name",
        "ticket_type__event__name",
        "ticket_type__event__partner__name",
        "ticket_type__name",
    ]


class TicketTypeAdminConfig(admin.ModelAdmin):
    search_fields = ["name", "event__name"]


class ReminderOptInAdminConfig(admin.ModelAdmin):
    search_fields = ["person__name", "event__name", "person__phone_number"]


admin.site.register(Event, EventAdminConfig)
admin.site.register(TicketType, TicketTypeAdminConfig)
admin.site.register(EventCategory, EventCategoryAdminConfig)
admin.site.register(EventPromotion, EventPromotionAdminConfig)
admin.site.register(TicketPromotion, TicketPromotionAdminConfig)
admin.site.register(ReminderOptIn, ReminderOptInAdminConfig)
