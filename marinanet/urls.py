from django.urls import path

from . import views

urlpatterns = [
    path('marinanet/ships', views.ship_list),
    path('marinanet/ships/<int:pk>', views.ShipDetail.as_view()),
]
