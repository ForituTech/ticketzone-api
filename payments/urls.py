from django.urls import path
from rest_framework.routers import DefaultRouter

from payments.views import PaymentsViewSet, fund_sms_package, list_payment_methods

router = DefaultRouter()

router.register("", viewset=PaymentsViewSet, basename="paymets")

urlpatterns = router.urls + [
    path("methods/", list_payment_methods, name="list_payment_methods"),
    path("fund/sms/package/", fund_sms_package, name="fund_sms_package"),
]
