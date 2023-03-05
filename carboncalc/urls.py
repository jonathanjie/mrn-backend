from django.urls import path

from . import views

urlpatterns=[
    path('cii/techinicalfiles/', views.EnergyEfficiencyTechnicalFileView.as_view()),
    path('cii/standarddatareporting/', views.StandardizedDataReportingFile.as_view()),
    path('cii/config/', views.CIIConfigView.as_view()),
    path('cii/ships-overview/', views.ShipsCIIOverviewListView.as_view()),
    path('cii/calculator/', views.CIICalculatorView.as_view()),
]
