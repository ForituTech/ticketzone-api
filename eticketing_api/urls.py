from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from eticketing_api.settings import API_VERSION_STRING

admin.site.site_header = "TicketZone Super-Admin"
admin.site.site_title = "TicketZone Super-Admin Portal"
admin.site.index_title = "Welcome to TicketZone Super-Admin Portal"


schema_view = get_schema_view(
    openapi.Info(
        title="TicketZone API",
        default_version="v1",
        description="TicketZone ticketing API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    re_path(
        r"$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(f"{API_VERSION_STRING}/admin/", admin.site.urls),
    path(f"{API_VERSION_STRING}/events/", include("events.urls")),
    path(f"{API_VERSION_STRING}/partner/", include("partner.urls")),
    path(f"{API_VERSION_STRING}/payments/", include("payments.urls")),
    path(f"{API_VERSION_STRING}/tickets/", include("tickets.urls")),
]
