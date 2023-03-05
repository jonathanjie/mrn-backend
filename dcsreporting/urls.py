from django.urls import path

from . import views

urlpatterns=[
    path('dcs/dcsfiles/', views.DCSUploadedFileView.as_view()),
]
