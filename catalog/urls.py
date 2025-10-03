from __future__ import annotations

from django.urls import path

from .views import AreaCodesView, SearchView

app_name = 'catalog'

urlpatterns = [
    path('area-codes/', AreaCodesView.as_view(), name='area-codes'),
    path('search/', SearchView.as_view(), name='search'),
]
