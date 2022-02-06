from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()

router.register(r"", viewset=views.EventVieset, basename="events")

urlpatterns = router.urls
