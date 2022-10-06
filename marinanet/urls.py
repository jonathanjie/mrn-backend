from django.urls import path

from . import views

urlpatterns = [
    path('marinanet/ships/', views.ShipList.as_view()),
    path('marinanet/ships/<int:imo_reg>/', views.ShipDetail.as_view()),
    path('marinanet/ships/<int:imo_reg>/voyages/',
         views.ShipVoyageList.as_view()),
    path('marinanet/voyages/', views.VoyageList.as_view()),
    path('marinanet/voyages/<int:pk>/', views.VoyageDetail.as_view()),
    path('marinanet/reports/<int:pk>/', views.NoonReport.as_view()),
]
