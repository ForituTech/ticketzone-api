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
    path(
        "events/redemtion-rate/",
        view=views.partner_redemtion_rate,
        name="redemtion-rate",
    ),
    path("sales/", view=views.partner_sales, name="sales"),
    path("events/ranked/", view=views.partner_ranked_events, name="ranked-events"),
    path(
        "events/tickets/<str:event_id>/",
        view=views.partner_event_ticket_with_sales,
        name="expanded-tickets",
    ),
]

urlpatterns += router.urls
