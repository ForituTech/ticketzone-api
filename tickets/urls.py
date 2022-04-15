from django.urls import path
from rest_framework.routers import DefaultRouter

from tickets import views

router = DefaultRouter()

router.register(r"", viewset=views.TicketViewSet, basename="tickets")
urlpatterns = [
    path("redeem/<str:pk>/", view=views.redeem_ticket, name="redeem_ticket"),
    path("search/<str:search_term>/", view=views.search_tickets, name="search_tickets"),
    path("by/hash/<str:hash>/", view=views.read_ticket_by_hash, name="ticket_by_hash"),
]

urlpatterns += router.urls
