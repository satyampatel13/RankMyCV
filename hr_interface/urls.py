from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_description, name='job_description'),
]
