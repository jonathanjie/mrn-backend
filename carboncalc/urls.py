from django.urls import path

from . import views

urlpatterns=p[
    path('cii/techinicalfile/upload/', views.EnergyEfficiencyTechnicalFileView.as_view()),
    path('cii/standardreporting/upload/', views.StandardizedDataReportingFile.as_view()),
]
