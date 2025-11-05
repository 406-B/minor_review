"""
list 应用的 URL 配置
定义所有 API 端点的路由
"""
from django.urls import path
from . import views

app_name = 'list'

urlpatterns = [
    # ==================== 食堂相关 ====================
    # GET /api/canteens/ - 获取食堂列表
    path('canteens/', views.canteen_list, name='canteen-list'),
    # GET /api/canteens/<id>/ - 获取食堂详情及菜品
    path('canteens/<int:canteen_id>/', views.canteen_detail, name='canteen-detail'),
    
    # ==================== 菜品相关 ====================
    # GET /api/dishes/ - 获取菜品列表
    path('dishes/', views.dish_list, name='dish-list'),
    # GET /api/dishes/<id>/ - 获取菜品详情
    path('dishes/<int:dish_id>/', views.dish_detail, name='dish-detail'),
    # GET /api/dishes/hot/ - 获取热门菜品
    path('dishes/hot/', views.hot_dishes, name='hot-dishes'),
    # GET /api/dishes/new/ - 获取新品菜品
    path('dishes/new/', views.new_dishes, name='new-dishes'),
    
    # ==================== 用户交互功能 ====================
    # POST /api/dishes/<id>/rate/ - 用户给菜品评分（需登录）
    path('dishes/<int:dish_id>/rate/', views.rate_dish, name='rate-dish'),
    # POST /api/dishes/<id>/tags/ - 给菜品添加标签（需登录）
    path('dishes/<int:dish_id>/tags/', views.add_tag_to_dish, name='add-tag-to-dish'),
    
    # ==================== 管理员功能 ====================
    # POST /api/dishes/<id>/tags/approve/ - 批准待审核标签（需管理员权限）
    path('dishes/<int:dish_id>/tags/approve/', views.approve_pending_tags, name='approve-pending-tags'),
    # POST /api/dishes/<id>/tags/reject/ - 拒绝待审核标签（需管理员权限）
    path('dishes/<int:dish_id>/tags/reject/', views.reject_pending_tags, name='reject-pending-tags'),
    
    # ==================== 标签相关 ====================
    # GET /api/tags/ - 获取所有标签
    path('tags/', views.tag_list, name='tag-list'),
    # POST /api/tags/create/ - 创建新标签（需管理员权限）
    path('tags/create/', views.create_tag, name='create-tag'),
]

