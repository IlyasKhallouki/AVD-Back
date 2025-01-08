from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('remove/', views.remove_file, name='remove_file'),
]