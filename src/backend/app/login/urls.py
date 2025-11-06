<<<<<<< HEAD

from django.urls import path
from . import views

urlpatterns = [
    path("user", views.get_user_info, name="get_user_info"),
    path("user/<int:userId>", views.get_user_info_by_id, name="get_user_info_by_id"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register_user, name="register"),
=======
from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/user", views.get_user_info, name="get_user_info"),
    path("api/v1/user/<int:userId>", views.get_user_info_by_id, name="get_user_info_by_id"),
    path("api/v1/login", views.LoginView.as_view(), name="login"),
    path("api/v1/logout", views.logout, name="logout"),
    path("api/v1/register", views.register_user, name="register"),
>>>>>>> origin/dev
]

