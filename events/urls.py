from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()

router.register(r"events", viewset=views.EventVieset, basename="events")
router.register(r"tickets", viewset=views.TicketTypeViewSet, basename="ticket_types")

urlpatterns = router.urls
