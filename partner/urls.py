from django.urls import path
from rest_framework.routers import DefaultRouter

from partner import views

router = DefaultRouter()
router.register(r"person", viewset=views.PersonViewSet, basename="person")
router.register(r"partner", viewset=views.PartnerViewSet, basename="partner")
router.register(
    r"partnership/person", viewset=views.PartnerPersonViewset, basename="partner_person"
)
router.register(r"sms", viewset=views.PartnerSMSPackageViewset, basename="sms_package")
router.register(r"promo", viewset=views.PartnerPromotionViewset, basename="promotion")

urlpatterns = [
    path("login/", view=views.login, name="login"),
    path(
        "events/redemtion-rate/",
        view=views.partner_redemtion_rate,
        name="redemtion-rate",
    ),
    path("sales/", view=views.partner_sales, name="sales"),
    path("revenue/", view=views.partner_sales_revenue, name="revenue"),
    path("events/ranked/", view=views.partner_ranked_events, name="ranked-events"),
    path(
        "events/tickets/<str:event_id>/",
        view=views.partner_event_ticket_with_sales,
        name="expanded-tickets",
    ),
    path(
        "promo/optin/<str:partner_id>/",
        view=views.partner_promo_optin,
        name="partner-promo-optin",
    ),
    path(
        "promo/optin/count/<str:partner_id>/",
        view=views.partner_promo_optin_count,
        name="partner-promo-optin-count",
    ),
]

urlpatterns += router.urls
