from django.urls import path

from . import views

urlpatterns = [
    path('marinanet/test', views.test),
    path('marinanet/reports/noon/submit', views.submit_noon_report)
]
