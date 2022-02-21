from django.urls import path
from rest_framework.routers import DefaultRouter

from partner import views

router = DefaultRouter()
router.register(r"person", viewset=views.PersonViewSet, basename="person")

urlpatterns = [path("login/", view=views.login, name="login")]

urlpatterns + router.urls
