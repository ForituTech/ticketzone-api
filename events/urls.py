from django.urls import path
from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()

router.register(r"events", viewset=views.EventViewset, basename="events")
router.register(r"tickets", viewset=views.TicketTypeViewSet, basename="ticket_types")

urlpatterns = [
    path("search/<str:search_term>/", view=views.search_events, name="event_search"),
]

urlpatterns += router.urls
