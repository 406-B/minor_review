"""
用户个人资料路由配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 个人资料管理
    path("profile", views.get_profile, name="get_profile"),
    path("profile/update", views.update_profile, name="update_profile"),
    path("profile/password", views.update_password, name="update_password"),
    # 用户统计信息
    path("profile/stats", views.get_stats, name="get_stats"),
    # 用户帖子相关
    path("profile/posts", views.get_my_posts, name="get_my_posts"),
    path("profile/posts/recent", views.get_recent_posts, name="get_recent_posts"),
    path("profile/posts/liked", views.get_liked_posts, name="get_liked_posts"),
    # 用户评论
    path("profile/comments", views.get_my_comments, name="get_my_comments"),
    # 用户偏好标签
    path("profile/preference-tags", views.get_preference_tags, name="get_preference_tags"),
    path("profile/preference-tags/set", views.set_preference_tags, name="set_preference_tags"),
    path("profile/preference-tags/add", views.add_preference_tags, name="add_preference_tags"),
    # 个性化推荐
    path("profile/recommended-dishes", views.get_recommended_dishes, name="get_recommended_dishes"),
    # 基于位置的推荐
    path("profile/nearby-dishes", views.get_nearby_recommended_dishes, name="get_nearby_recommended_dishes"),
]
