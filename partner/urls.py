from django.urls import path
from rest_framework.routers import DefaultRouter

from partner import views

router = DefaultRouter()

urlpatterns = [path("login/", view=views.login, name="login")]
