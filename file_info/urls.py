from django.urls import path
from . import views

urlpatterns = [
    path('describe/', views.describe_csv, name='describe_csv'),
    path('head/', views.head_csv, name='head_csv'),
    path('columns/', views.column_names, name='column_names'),
    path('shape/', views.shape_csv, name='shape_csv'),
    path('get_rows_or_columns/', views.get_rows_or_columns, name='get_rows_or_columns'),
    path('column_stats/', views.column_statistics, name='column_statistics'),

    path('aggregate_info/', views.aggregate_csv_info, name='aggregate_csv_info'),
]
