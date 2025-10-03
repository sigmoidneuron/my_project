from __future__ import annotations

from django.urls import path

from .views import (
    DashboardLoginView,
    DashboardLogoutView,
    delete_all,
    home,
    phone_create,
    phone_delete,
    phone_update,
    update_password,
    upload_csv,
)

app_name = 'dashboard'

urlpatterns = [
    path('login/', DashboardLoginView.as_view(), name='login'),
    path('logout/', DashboardLogoutView.as_view(), name='logout'),
    path('', home, name='home'),
    path('create/', phone_create, name='create'),
    path('<int:pk>/edit/', phone_update, name='update'),
    path('<int:pk>/delete/', phone_delete, name='delete'),
    path('delete-all/', delete_all, name='delete-all'),
    path('upload/', upload_csv, name='upload'),
    path('password/', update_password, name='password'),
]
