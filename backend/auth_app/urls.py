from django.urls import path
from . import views

urlpatterns = [
    path("auth/csrf-token/", views.csrf_token, name="csrf_token"),
    path("auth/register/start/", views.register_start, name="register_start"),
    path("auth/register/complete/", views.register_complete, name="register_complete"),
    path("auth/login/start/", views.login_start, name="login_start"),
    path("auth/login/complete/", views.login_complete, name="login_complete"),
    path("auth/user/", views.user_info, name="user_info"),
    path("auth/logout/", views.logout, name="logout"),
]
