from django.urls import path
from . import views

urlpatterns = [
    path("user", views.get_user_info, name="get_user_info"),
    path("user/<int:userId>", views.get_user_info_by_id, name="get_user_info_by_id"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register_user, name="register"),
]

