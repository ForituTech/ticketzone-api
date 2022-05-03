from django.urls import path
from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()

router.register(r"events", viewset=views.EventViewset, basename="events")
router.register(r"tickets", viewset=views.TicketTypeViewSet, basename="ticket_types")
router.register(
    r"event/promo", viewset=views.EventPromotionViewset, basename="event_promos"
)
router.register(
    r"ticket/promo", viewset=views.TicketTypePromotionViewset, basename="ticket_promo"
)

urlpatterns = [
    path("redeem/code/<str:code>/", view=views.redeem_promo_code, name="reedeem_code"),
    path("categories/", views.list_categories, name="categoreis"),
    path(
        "reminder/optin/<str:event_id>/",
        view=views.event_reminder_optin,
        name="event-reminder-optin",
    ),
    path("highlighted/", views.highlighted_events, name="highlighted_events"),
]

urlpatterns += router.urls
