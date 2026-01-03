from django.urls import path
from . import views

urlpatterns = [
    # 论坛主页
    path('forum/home/', views.forum_home, name='forum_home'),
    
    # 菜品相关帖子
    path('dishes/<int:dish_id>/posts/', views.dish_posts, name='dish_posts'),
    
    # 图片上传
    path('upload/image/', views.upload_image, name='upload_image'),
    
    # 帖子相关
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    
    # 评论相关
    path('posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('comments/create/', views.create_comment, name='create_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]
