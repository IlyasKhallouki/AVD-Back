from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('remove/', views.remove_file, name='remove_file'),
    path('', views.retreive_files, name='retreive_files'),
    path('meta/', views.get_file_info, name='get_file_info')
]