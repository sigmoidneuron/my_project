"""phonebook URL Configuration."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls', namespace='catalog_api')),
    path('', include('dashboard.urls', namespace='dashboard')),
]
