from django.urls import path
from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()

router.register(r"events", viewset=views.EventViewset, basename="events")
router.register(r"tickets", viewset=views.TicketTypeViewSet, basename="ticket_types")
router.register(
    r"event/promo", viewset=views.EventPromotionViewset, basename="event_promos"
)

urlpatterns = [
    path("categories/", views.list_categories, name="categoreis"),
    path(
        "reminder/optin/<str:event_id>/",
        view=views.event_reminder_optin,
        name="event-reminder-optin",
    ),
    path("highlighted/", views.highlighted_events, name="highlighted_events"),
    path(
        "partner/count/<str:partner_id>/",
        view=views.get_total_events_for_partner,
        name="partner_events_count",
    ),
    path("export/csv/", view=views.export_events, name="export_events"),
    path("validate/<str:event_id>/promo/<str:code>/", view=views.validate_promocode),
]

urlpatterns += router.urls
