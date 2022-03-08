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
    path("search/<str:search_term>/", view=views.search_events, name="event_search"),
    path("redeem/code/<str:code>/", view=views.redeem_promo_code, name="reedeem_code"),
]

urlpatterns += router.urls
