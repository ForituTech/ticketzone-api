from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

admin.site.site_header = "Eticketing Super-Admin"
admin.site.site_title = "Eticketing Super-Admin Portal"
admin.site.index_title = "Welcome to Eticketing Super-Admin Portal"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),
    path(
        "openapi",
        get_schema_view(
            title="Eticketing-API",
            description="Engine for ticket management …",
            version="0.1.0",
        ),
        name="openapi-schema",
    ),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        TemplateView.as_view(
            template_name="redoc.html", extra_context={"schema_url": "openapi-schema"}
        ),
        name="redoc",
    ),
]
