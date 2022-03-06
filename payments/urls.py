from rest_framework.routers import DefaultRouter

from payments.views import PaymentsViewSet

router = DefaultRouter()

router.register("", viewset=PaymentsViewSet, basename="paymets")

urlpatterns = router.urls
