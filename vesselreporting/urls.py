from django.urls import path

from . import views

urlpatterns = [
    path('marinanet/ships/', views.ShipList.as_view()), # Unused
    path('marinanet/ships-overview/', views.ShipsOverviewListView.as_view()),
    path('marinanet/ships/<int:imo_reg>/', views.ShipDetail.as_view()),
    path('marinanet/ships/<int:imo_reg>/specs/',
         views.ShipSpecsCreateView.as_view()),
    path('marinanet/ships/<int:imo_reg>/voyages/', # Unused
         views.ShipVoyageList.as_view()),
    path('marinanet/ships/<int:imo_reg>/latest-voyage/', # Unused
         views.LatestVoyageDetailByShip.as_view()),
    path('marinanet/ships/<int:imo_reg>/reports/',
         views.ShipReportsList.as_view()),
    path('marinanet/ships/<int:imo_reg>/latest-report/', # Unused
         views.LatestReportDetailByShip.as_view()),
    path('marinanet/ships/<int:imo_reg>/legs/', views.ShipLegsList.as_view()),
    path('marinanet/ships/<int:imo_reg>/latest-details/',
         views.ReportPrefillView.as_view()),
    path('marinanet/voyages/', views.VoyageList.as_view()),
    path('marinanet/voyages/<uuid:uuid>/', views.VoyageDetail.as_view()), # Unused
    path('marinanet/voyages/<uuid:uuid>/reports/', # Unused
         views.VoyageReportsList.as_view()),
    path('marinanet/voyagelegs/', views.VoyageLegList.as_view()),
    path('marinanet/reports/', views.ReportsList.as_view()), # Unused
    path('marinanet/reports/<uuid:uuid>/', views.ReportDetail.as_view()),
    path('marinanet/ships/<int:imo_reg>/stats/',
         views.WeeklyStatsList.as_view()),
    path('marinanet/user/', views.UserProfileView.as_view()),
]
