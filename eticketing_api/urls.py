from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

admin.site.site_header = "Eticketing Super-Admin"
admin.site.site_title = "Eticketing Super-Admin Portal"
admin.site.index_title = "Welcome to Eticketing Super-Admin Portal"


schema_view = get_schema_view(
    openapi.Info(
        title="Ticketzone API",
        default_version="v1",
        description="Ticketing Engine",
        contact=openapi.Contact(email="mogendi.mongare@gmail.com"),
        license=openapi.License(name="BSD License"),
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
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),
    path("partner/", include("partner.urls")),
    path("payments/", include("payments.urls")),
    path("", include("tickets.urls")),
]
