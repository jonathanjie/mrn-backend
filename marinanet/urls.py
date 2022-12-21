from django.urls import path

from . import views

urlpatterns = [
    path('marinanet/ships/', views.ShipList.as_view()),
    path('marinanet/ships/<int:imo_reg>/', views.ShipDetail.as_view()),
    path('marinanet/ships/<int:imo_reg>/specs/', views.ShipSpecsCreate.as_view()),
    path('marinanet/ships/<int:imo_reg>/voyages/',
         views.ShipVoyageList.as_view()),
    path('marinanet/ships/<int:imo_reg>/reports/',
         views.ShipReportsList.as_view()),
    path('marinanet/ships/<int:imo_reg>/latest-report', views.LatestReportDetailByShip.as_view()),
    # path('marinanet/ships/<int:imo_reg>/most-recent-distinct-routes/', views.MostRecentDistinctRoutesList.as_view()),
    path('marinanet/voyages/', views.VoyageList.as_view()),
    path('marinanet/voyages/<uuid:uuid>/', views.VoyageDetail.as_view()),
    path('marinanet/voyages/<uuid:uuid>/reports',
         views.VoyageReportsList.as_view()),
    path('marinanet/reports/', views.ReportsList.as_view()),
    path('marinanet/reports/<uuid:uuid>/', views.ReportDetail.as_view()),
    path('marinanet/user/', views.UserProfileView.as_view()),
]
