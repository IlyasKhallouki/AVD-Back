from django.urls import path
from . import views

urlpatterns = [
    path('visualize/', views.visualize_data, name='visualize_data')
]
