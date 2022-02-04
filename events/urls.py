from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from events import views

urlpatterns = [
    path("", views.list_events),
]

urlpatterns = format_suffix_patterns(urlpatterns)
