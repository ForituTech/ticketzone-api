from django.urls import path

from events import views

urlpatterns = [
    path("", views.list_events),
    path("<int:event_id>/", views.get_event),
    path("create/", views.create_event),
    path("update/", views.update_event),
]
