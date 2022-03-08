from rest_framework.routers import DefaultRouter

from tickets import views

router = DefaultRouter()

router.register(r"tickets", viewset=views.TicketViewSet, basename="tickets")

urlpatterns = router.urls
