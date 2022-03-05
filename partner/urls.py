from django.urls import path
from rest_framework.routers import DefaultRouter

from partner import views

router = DefaultRouter()
router.register(r"person", viewset=views.PersonViewSet, basename="person")
router.register(r"partner", viewset=views.PartnerViewSet, basename="partner")
router.register(
    r"partnership/person", viewset=views.PartnerPersonViewset, basename="partner_person"
)

urlpatterns = [
    path("login/", view=views.login, name="login"),
]

urlpatterns += router.urls
