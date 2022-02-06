"""eticketing_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('openapi', get_schema_view(
        title="Eticketing-API",
        description="Engine for ticket management …",
        version="0.1.0"
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]
