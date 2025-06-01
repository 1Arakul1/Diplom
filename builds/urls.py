# builds/urls.py

from django.urls import path
from . import views

app_name = 'builds'

urlpatterns = [
    path('', views.build_list, name='build_list'),
    path('<int:pk>/', views.build_detail, name='build_detail'),
    path('create/', views.build_create, name='build_create'),
]