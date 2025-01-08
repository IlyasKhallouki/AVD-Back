from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('upload/', include('file_upload.urls')),
    path('admin/', admin.site.urls),
]
