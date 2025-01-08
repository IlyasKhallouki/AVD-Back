from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('file/', include('file_upload.urls')),
    path('file/', include('file_info.urls')),
    path('admin/', admin.site.urls),
]
