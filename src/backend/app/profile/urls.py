"""
用户个人资料路由配置
"""
from django.urls import path

from . import views

urlpatterns = [
    # 个人资料管理
    path("api/v1/profile", views.get_profile, name="get_profile"),
    path("api/v1/profile/update", views.update_profile, name="update_profile"),
    path("api/v1/profile/password", views.update_password, name="update_password"),
    # 用户统计信息
    path("api/v1/profile/stats", views.get_stats, name="get_stats"),
]
