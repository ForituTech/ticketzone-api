from django.contrib import admin

from .models import Event, EventCategory, EventPromotion, TicketPromotion, TicketType

admin.site.register([Event, EventPromotion, TicketType, TicketPromotion, EventCategory])
