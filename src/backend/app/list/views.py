from .models import Floor, Window
from .serializers import FloorSerializer
# ==================== 食堂楼层与窗口接口 ====================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def canteen_floors(request, canteen_id):
    """
    获取指定食堂的所有楼层、窗口及窗口下的菜品
    """
    floors = Floor.objects.filter(canteen_id=canteen_id).order_by('order', 'id')
    data = FloorSerializer(floors, many=True).data
    return Response({
        'code': 200,
        'message': '获取楼层窗口成功',
        'data': data
    })
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q, Count
from .models import Canteen, Dish, Tag, Rating, Review, UserDishHistory, DishCheckInRecord
from django.contrib.auth.models import User as AuthUser
from .serializers import (
    CanteenSerializer, DishSerializer, DishListSerializer, TagSerializer,
    RatingSerializer, ReviewSerializer, ReviewListSerializer,
    UserDishHistorySerializer, UserDishHistoryListSerializer
)

# ============== 辅助方法：确保获取到 Django AuthUser ==============
def _get_or_create_auth_user(request):
    """将自定义登录用户统一映射到 Django 内置 AuthUser。
    返回 AuthUser 或 None（当拿不到用户名时）。
    """
    try:
        if isinstance(request.user, AuthUser):
            return request.user
        username = getattr(request.user, 'username', None)
        if not username:
            return None
        user, _created = AuthUser.objects.get_or_create(username=username, defaults={"password": ""})
        return user
    except Exception:
        return None

# ==================== 我的评论视图 ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_reviews(request):
    """
    获取当前登录用户的所有评论
    支持分页和排序
    """
    # 将自定义 login.User 映射为 Django AuthUser（Rating/Review 外键依赖）
    if isinstance(request.user, AuthUser):
        auth_user = request.user
    else:
        auth_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not auth_user and getattr(request.user, 'username', None):
            auth_user = AuthUser.objects.create(username=request.user.username)
    reviews = Review.objects.filter(user=auth_user)

    # 排序
    ordering = request.query_params.get('ordering', '-created_at')
    if ordering in ['created_at', '-created_at', 'likes_count', '-likes_count']:
        reviews = reviews.order_by(ordering)

    # 分页（可选）
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    start = (page - 1) * page_size
    end = start + page_size
    paged_reviews = reviews[start:end]

    serializer = ReviewListSerializer(paged_reviews, many=True)
    return Response({
        'code': 200,
        'message': '获取我的评论成功',
        'data': {
            'reviews': serializer.data,
            'total': reviews.count(),
            'page': page,
            'page_size': page_size
        }
    })


# ==================== 食堂列表与详情 ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def canteen_list(request):
    queryset = Canteen.objects.all()

    # 搜索功能
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(name__icontains=search)

    # 排序
    ordering = request.query_params.get('ordering', 'name')
    if ordering in ['name', '-name', 'created_at', '-created_at']:
        queryset = queryset.order_by(ordering)

    serializer = CanteenSerializer(queryset, many=True)
    return Response({
        'code': 200,
        'message': '获取食堂列表成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def canteen_detail(request, canteen_id):
    """
    获取食堂详情及其所有菜品
    包含该食堂的所有菜品列表
    """
    canteen = get_object_or_404(Canteen, id=canteen_id)

    # 获取该食堂的所有菜品
    dishes = Dish.objects.filter(canteen=canteen)

    # 支持按标签筛选
    tag_ids = request.query_params.getlist('tag_ids', None)
    if tag_ids:
        for tag_id in tag_ids:
            dishes = dishes.filter(tags__id=tag_id)
        dishes = dishes.distinct()
    # 支持按评分筛选
    min_rating = request.query_params.get('min_rating', None)
    if min_rating:
        dishes = dishes.filter(rating__gte=float(min_rating))

    # 支持关键词搜索（搜索菜品名称、描述、食堂名称、标签名称）
    search = request.query_params.get('search', None)
    if search:
        dishes = dishes.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(canteen__name__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()  # 去重，因为标签可能匹配多次

    # 排序
    ordering = request.query_params.get('ordering', '-rating')
    if ordering in ['rating', '-rating', 'view_count', '-view_count', 'price', '-price', 'name', '-name']:
        dishes = dishes.order_by(ordering)

    canteen_serializer = CanteenSerializer(canteen)
    dishes_serializer = DishListSerializer(dishes, many=True)

    return Response({
        'code': 200,
        'message': '获取食堂详情成功',
        'data': {
            'canteen': canteen_serializer.data,
            'dishes': dishes_serializer.data,
            'dish_count': dishes.count()
        }
    })


# ==================== 菜品相关视图 ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dish_list(request):
    """
    获取所有菜品列表
    支持多种筛选和排序
    """
    queryset = Dish.objects.all()

    # 按食堂筛选
    canteen_id = request.query_params.get('canteen_id', None)
    if canteen_id:
        queryset = queryset.filter(canteen_id=canteen_id)

    # 按标签筛选（支持多个标签）
    tag_ids = request.query_params.getlist('tag_ids', None)
    if tag_ids:
        for tag_id in tag_ids:
            queryset = queryset.filter(tags__id=tag_id)
        queryset = queryset.distinct()

    # 按评分筛选
    min_rating = request.query_params.get('min_rating', None)
    if min_rating:
        queryset = queryset.filter(rating__gte=float(min_rating))

    # 按价格筛选
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)
    if min_price:
        queryset = queryset.filter(price__gte=float(min_price))
    if max_price:
        queryset = queryset.filter(price__lte=float(max_price))

    # 关键词搜索（搜索菜品名称、描述、食堂名称、标签名称）
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(canteen__name__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()  # 去重，因为标签可能匹配多次

    # 排序
    ordering = request.query_params.get('ordering', '-rating')
    if ordering in ['rating', '-rating', 'view_count', '-view_count', 'price', '-price', 'name', '-name']:
        queryset = queryset.order_by(ordering)

    serializer = DishListSerializer(queryset, many=True)
    return Response({
        'code': 200,
        'message': '获取菜品列表成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dish_detail(request, dish_id):
    """
    获取菜品详情
    自动增加浏览次数
    """
    dish = get_object_or_404(Dish, id=dish_id)

    # 增加浏览次数
    dish.increment_view_count()

    serializer = DishSerializer(dish)
    return Response({
        'code': 200,
        'message': '获取菜品详情成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def hot_dishes(request):
    """
    获取热门菜品（按浏览次数排序）
    """
    limit = int(request.query_params.get('limit', 10))
    dishes = Dish.objects.order_by('-view_count', '-rating')[:limit]

    serializer = DishListSerializer(dishes, many=True)
    return Response({
        'code': 200,
        'message': '获取热门菜品成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def new_dishes(request):
    """
    获取新上线菜品
    """
    limit = int(request.query_params.get('limit', 10))
    dishes = Dish.objects.order_by('-created_at')[:limit]

    serializer = DishListSerializer(dishes, many=True)
    return Response({
        'code': 200,
        'message': '获取新品菜品成功',
        'data': serializer.data
    })


# ==================== 用户交互功能 ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_dish(request, dish_id):
    """
    用户给菜品评分
    需要提供评分值（1-5分）

    请求体示例：
    {
        "rating": 4.5
    }

    注意：这是简化版本，实际应该记录每个用户的评分，然后计算平均值
    """
    dish = get_object_or_404(Dish, id=dish_id)
    # 映射用户
    if isinstance(request.user, AuthUser):
        auth_user = request.user
    else:
        auth_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not auth_user and getattr(request.user, 'username', None):
            auth_user = AuthUser.objects.create(username=request.user.username)

    rating_value = request.data.get('rating')
    if not rating_value:
        return Response({
            'code': 400,
            'message': '请提供评分值',
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating_value = float(rating_value)
        if rating_value < 0 or rating_value > 5:
            return Response({
                'code': 400,
                'message': '评分必须在0-5之间',
            }, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({
            'code': 400,
            'message': '评分格式不正确',
        }, status=status.HTTP_400_BAD_REQUEST)

    # 检查用户是否已经评过分，以便计算增量更新
    old_user_rating = None
    try:
        existing_rating = Rating.objects.get(dish=dish, user=auth_user)
        old_user_rating = float(existing_rating.score)
    except Rating.DoesNotExist:
        pass
    
    # 创建或更新用户对该菜品的评分（Rating表字段为 score，不是 rating）
    rating_obj, created = Rating.objects.update_or_create(dish=dish, user=auth_user, defaults={'score': rating_value})

    # 使用增量更新方式计算新评分
    # 新评分 = (旧评分 × 旧评分人数 + 新评分) / (旧评分人数 + 1)
    old_rating = float(dish.rating) if dish.rating else 0.0
    old_rating_count = dish.rating_count
    
    if created:
        # 新用户评分：评分人数+1
        new_rating_count = old_rating_count + 1
        new_rating = (old_rating * old_rating_count + rating_value) / new_rating_count
    else:
        # 用户修改评分：评分人数不变，但需要用新评分替换旧评分
        # 计算：先减去旧评分的贡献，再加上新评分
        if old_rating_count > 0 and old_user_rating is not None:
            new_rating = (old_rating * old_rating_count - old_user_rating + rating_value) / old_rating_count
            new_rating_count = old_rating_count
        else:
            # 异常情况：评分人数为0但有评分记录，重置为1
            new_rating = rating_value
            new_rating_count = 1
    
    # 更新菜品的评分和评分人数
    dish.rating = round(new_rating, 2)
    dish.rating_count = new_rating_count
    dish.save(update_fields=['rating', 'rating_count'])

    return Response({
        'code': 200,
        'message': '评分成功' if created else '已更改评分',
        'data': {
            'dish_id': dish.id,
            'user_score': float(rating_obj.score),
            'new_rating': float(dish.rating),
            'rating_count': dish.rating_count
        }
    })

    # 若用户已评论该菜品但评论尚未关联评分，尝试关联
    user_review = Review.objects.filter(user=auth_user, dish=dish, rating__isnull=True).first()
    if user_review:
        user_review.rating = rating_obj
        user_review.save(update_fields=['rating'])


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_tag_to_dish(request, dish_id):
    """
    用户给菜品添加标签
    - AI审核通过后直接添加到tags（暂时停用人工审核）
    
    # 已注释：原人工审核流程
    # - 普通用户：标签添加到pending_tags（待审核）
    # - 管理员：标签直接添加到tags

    请求体示例：
    {
        "tag_ids": [1, 2, 3]  # 现有标签ID列表
    }
    或者
    {
        "tag_name": "新标签名称"  # 创建新标签并添加
    }
    """
    dish = get_object_or_404(Dish, id=dish_id)
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user and getattr(request.user, 'username', None):
            user = AuthUser.objects.create(username=request.user.username)

    # 检查输入
    tag_ids = request.data.get('tag_ids', [])
    tag_name = request.data.get('tag_name')

    if not tag_ids and not tag_name:
        return Response({
            'code': 400,
            'message': '请提供tag_ids或tag_name',
        }, status=status.HTTP_400_BAD_REQUEST)

    message = ''

    # 处理现有标签 - 直接添加（已停用人工审核）
    if tag_ids:
        tags = Tag.objects.filter(id__in=tag_ids)
        
        # 所有用户直接添加到tags（暂时停用人工审核）
        for tag in tags:
            if tag not in dish.tags.all():
                dish.tags.add(tag)
        message = '标签添加成功'
        
        # # 原人工审核流程（已注释）
        # if user.is_staff or user.is_superuser:
        #     # 管理员直接添加到tags
        #     for tag in tags:
        #         if tag not in dish.tags.all():
        #             dish.tags.add(tag)
        #     message = '标签添加成功'
        # else:
        #     # 普通用户添加到pending_tags
        #     for tag in tags:
        #         if tag not in dish.pending_tags.all():
        #             dish.pending_tags.add(tag)
        #     message = '标签已提交，等待管理员审核'

    # 处理新标签 - AI审核通过后直接添加
    if tag_name:
        tag_name_trimmed = tag_name.strip()
        
        # 对新标签名称进行AI内容审核
        from utils.audit import audit_content
        is_passed, reason = audit_content(
            content=tag_name_trimmed,
            content_type='tag',
            title=''
        )
        
        # 如果AI审核未通过，直接拒绝
        if not is_passed:
            return Response({
                'code': 400,
                'message': f'标签名称审核未通过: {reason}',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # AI审核通过，创建标签并直接添加（暂时停用人工审核）
        tag, created = Tag.objects.get_or_create(name=tag_name_trimmed)
        
        # 所有用户直接添加到tags（暂时停用人工审核）
        if tag not in dish.tags.all():
            dish.tags.add(tag)
        message = '标签添加成功' if not message else message
        
        # # 原人工审核流程（已注释）
        # if user.is_staff or user.is_superuser:
        #     if tag not in dish.tags.all():
        #         dish.tags.add(tag)
        #     message = '标签添加成功'
        # else:
        #     if tag not in dish.pending_tags.all():
        #         dish.pending_tags.add(tag)
        #     message = '标签已提交，等待管理员审核'

    serializer = DishSerializer(dish)
    return Response({
        'code': 200,
        'message': message,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_pending_tags(request, dish_id):
    """
    管理员审核并批准待审核的标签
    将pending_tags移动到tags

    请求体示例：
    {
        "tag_ids": [1, 2]  # 要批准的标签ID列表，留空则批准所有
    }
    """
    dish = get_object_or_404(Dish, id=dish_id)
    if not isinstance(request.user, AuthUser):
        # 管理员校验仍需使用 auth_user 对象
        admin_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not admin_user and getattr(request.user, 'username', None):
            admin_user = AuthUser.objects.create(username=request.user.username)

    tag_ids = request.data.get('tag_ids', [])

    if tag_ids:
        # 批准指定的标签
        tags = dish.pending_tags.filter(id__in=tag_ids)
    else:
        # 批准所有待审核标签
        tags = dish.pending_tags.all()

    approved_count = 0
    for tag in tags:
        if tag not in dish.tags.all():
            dish.tags.add(tag)
        dish.pending_tags.remove(tag)
        approved_count += 1

    serializer = DishSerializer(dish)
    return Response({
        'code': 200,
        'message': f'成功批准{approved_count}个标签',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def reject_pending_tags(request, dish_id):
    """
    管理员拒绝待审核的标签
    从pending_tags中移除

    请求体示例：
    {
        "tag_ids": [1, 2]  # 要拒绝的标签ID列表
    }
    """
    dish = get_object_or_404(Dish, id=dish_id)
    if not isinstance(request.user, AuthUser):
        admin_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not admin_user and getattr(request.user, 'username', None):
            admin_user = AuthUser.objects.create(username=request.user.username)

    tag_ids = request.data.get('tag_ids', [])
    if not tag_ids:
        return Response({
            'code': 400,
            'message': '请提供要拒绝的标签ID列表',
        }, status=status.HTTP_400_BAD_REQUEST)

    tags = dish.pending_tags.filter(id__in=tag_ids)
    rejected_count = 0
    for tag in tags:
        dish.pending_tags.remove(tag)
        rejected_count += 1

    serializer = DishSerializer(dish)
    return Response({
        'code': 200,
        'message': f'成功拒绝{rejected_count}个标签',
        'data': serializer.data
    })


# ==================== 标签相关视图 ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tag_list(request):
    """
    获取所有标签列表
    """
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response({
        'code': 200,
        'message': '获取标签列表成功',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_tag(request):
    """
    创建新标签（管理员）

    请求体示例：
    {
        "name": "辣"
    }
    """
    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        tag_name = serializer.validated_data['name']

        # 审核标签名称
        from utils.audit import audit_content
        is_passed, reason = audit_content(
            content=tag_name,
            content_type='tag_name',
            title='标签名称'
        )

        if not is_passed:
            return Response({
                'code': 400,
                'message': f'标签名称审核未通过: {reason}'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            'code': 201,
            'message': '标签创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'code': 400,
        'message': '标签创建失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==================== 评论相关视图 ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def review_list(request, dish_id):
    """
    获取指定菜品的评论列表
    支持关键词搜索：搜索评论内容、用户名
    支持排序：按时间(默认)、点赞数
    """
    dish = get_object_or_404(Dish, id=dish_id)
    reviews = Review.objects.filter(dish=dish)

    # 关键词搜索（搜索评论内容、用户名）
    search = request.query_params.get('search', None)
    if search:
        reviews = reviews.filter(
            Q(content__icontains=search) |
            Q(user__username__icontains=search)
        )

    # 排序
    ordering = request.query_params.get('ordering', '-created_at')
    if ordering in ['created_at', '-created_at', 'likes_count', '-likes_count']:
        reviews = reviews.order_by(ordering)

    serializer = ReviewListSerializer(reviews, many=True)
    return Response({
        'code': 200,
        'message': '获取评论列表成功',
        'data': {
            'dish_id': dish.id,
            'reviews': serializer.data,
            'total': reviews.count()
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_review(request, dish_id):
    """
    用户创建评论

    请求体示例：
    {
        "content": "很好吃！",
        "images": ["http://example.com/1.jpg", "http://example.com/2.jpg"],
        "rating_score": 4.5  # 可选，如果提供则同时创建或更新评分
    }
    """
    dish = get_object_or_404(Dish, id=dish_id)
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user and getattr(request.user, 'username', None):
            user = AuthUser.objects.create(username=request.user.username)

    # 评论前必须已完成评分；取当前评分作为评分快照
    rating_obj = Rating.objects.filter(user=user, dish=dish).first()
    if not rating_obj:
        return Response({
            'code': 400,
            'message': '您需要先完成评分'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 若前端未传 images，设为空列表避免验证错误
    incoming_data = request.data.copy()
    if 'images' not in incoming_data or incoming_data.get('images') in [None, '']:
        incoming_data['images'] = []
    
    serializer = ReviewSerializer(data=incoming_data, context={'request': request})
    if serializer.is_valid():
        # 先进行内容审核（在创建之前）
        from utils.audit import audit_content
        
        content = serializer.validated_data['content']
        is_passed, reason = audit_content(
            content=content,
            content_type='review',
            title=f'评价: {dish.name}'
        )

        # 如果审核未通过，直接返回错误，不保存到数据库
        if not is_passed:
            return Response({
                'code': 400,
                'message': f'评论创建失败，内容审核未通过: {reason}',
            }, status=status.HTTP_400_BAD_REQUEST)

        # 审核通过，创建评论
        review = serializer.save(user=user, dish=dish, rating=rating_obj, published_score=rating_obj.score)

        # 设置为已审核通过状态
        from django.utils import timezone
        review.status = 'approved'
        review.audited_at = timezone.now()
        review.save()

        return Response({
            'code': 201,
            'message': '评论创建成功',
            'data': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '评论创建失败',
        'errors': serializer.errors,
        # 调试信息（DEBUG 模式下返回，生产应移除）
        'debug': {
            'incoming_keys': list(incoming_data.keys()),
            'raw_data': incoming_data,
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_review(request, review_id):
    """
    用户更新自己的评论

    请求体示例（可部分更新）：
    {
        "content": "更新后的内容",
        "images": ["http://example.com/new.jpg"]
    }
    """
    review = get_object_or_404(Review, id=review_id)
    if not isinstance(request.user, AuthUser):
        auth_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not auth_user and getattr(request.user, 'username', None):
            auth_user = AuthUser.objects.create(username=request.user.username)
    else:
        auth_user = request.user

    # 检查权限：只能编辑自己的评论
    if review.user != auth_user:
        return Response({
            'code': 403,
            'message': '您没有权限编辑此评论'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'code': 200,
            'message': '评论更新成功',
            'data': serializer.data
        })

    return Response({
        'code': 400,
        'message': '评论更新失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_review(request, review_id):
    """
    用户删除自己的评论
    管理员可以删除任何评论
    """
    review = get_object_or_404(Review, id=review_id)
    if not isinstance(request.user, AuthUser):
        auth_user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not auth_user and getattr(request.user, 'username', None):
            auth_user = AuthUser.objects.create(username=request.user.username)
    else:
        auth_user = request.user

    # 检查权限：只能删除自己的评论，或者管理员
    if review.user != auth_user and not (getattr(auth_user, 'is_staff', False) or getattr(auth_user, 'is_superuser', False)):
        return Response({
            'code': 403,
            'message': '您没有权限删除此评论'
        }, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({
        'code': 200,
        'message': '评论删除成功'
    })


# ==================== 评论点赞功能 ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_review(request, review_id):
    """
    用户点赞/取消点赞评论
    - 如果用户已点赞，则取消点赞
    - 如果用户未点赞，则点赞
    返回当前点赞状态和点赞数
    """
    review = get_object_or_404(Review, id=review_id)
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user and getattr(request.user, 'username', None):
            user = AuthUser.objects.create(username=request.user.username)

    # 假设有一个ReviewLike模型用于记录用户点赞（如未建表可用set模拟，或直接在Review模型加ManyToManyField）
    # 这里用最简单的方式：在session中模拟（生产环境应建表）
    # 推荐后续扩展ReviewLike模型
    if not hasattr(review, '_liked_users'):
        # 临时属性，实际应为数据库字段
        review._liked_users = set()

    # 用session模拟点赞（仅演示，实际应用请用数据库）
    liked_key = f'review_liked_{review_id}'
    liked = request.session.get(liked_key, False)

    if liked:
        # 取消点赞
        review.likes_count = max(0, review.likes_count - 1)
        request.session[liked_key] = False
        review.save(update_fields=['likes_count'])
        return Response({
            'code': 200,
            'message': '已取消点赞',
            'liked': False,
            'likes_count': review.likes_count
        })
    else:
        # 点赞
        review.likes_count += 1
        request.session[liked_key] = True
        review.save(update_fields=['likes_count'])
        return Response({
            'code': 200,
            'message': '点赞成功',
            'liked': True,
            'likes_count': review.likes_count
        })


# ==================== 用户菜品历史（打卡功能） ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_in_dish(request, dish_id):
    """
    打卡菜品（记录用户吃过这道菜）
    每次调用会增加该菜品的打卡次数
    """
    dish = get_object_or_404(Dish, id=dish_id)
    user = _get_or_create_auth_user(request)
    if not user:
        return Response({
            'code': 401,
            'message': '未登录或无效用户'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # 限制：每道菜每天最多打卡3次
    from django.utils import timezone
    today = timezone.now().date()
    today_count = DishCheckInRecord.objects.filter(
        user=user,
        dish=dish,
        checked_in_at__date=today
    ).count()

    if today_count >= 3:
        return Response({
            'code': 400,
            'message': '同一道菜每日最多打卡3次'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取打卡备注（可选）
    notes = request.data.get('notes', '')

    # 创建打卡记录（用于美食日历）
    check_in_record = DishCheckInRecord.objects.create(
        user=user,
        dish=dish,
        notes=notes
    )

    # 获取或创建历史记录（用于统计）
    history, created = UserDishHistory.objects.get_or_create(
        user=user,
        dish=dish,
        defaults={'count': 0}
    )

    # 增加打卡次数
    history.increment_count()

    # 序列化返回
    serializer = UserDishHistorySerializer(history)

    message = f'打卡成功！这是您第 {history.count} 次品尝"{dish.name}"'
    if created or history.count == 1:
        message += f'，恭喜获得【{history.level_display}】称号！'
    elif history.count in [3, 10, 100]:
        message += f'，恭喜晋升为【{history.level_display}】！'

    return Response({
        'code': 200,
        'message': message,
        'data': {
            **serializer.data,
            'check_in_record_id': check_in_record.id,
            'checked_in_at': check_in_record.checked_in_at
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_dish_history(request):
    """
    获取用户的菜品历史记录
    支持筛选和排序
    """
    user = _get_or_create_auth_user(request)
    if not user:
        return Response({
            'code': 404,
            'message': '用户不存在',
            'data': []
        }, status=status.HTTP_404_NOT_FOUND)

    histories = UserDishHistory.objects.filter(user=user)

    # 按级别筛选
    level = request.query_params.get('level', None)
    if level:
        # 根据级别筛选
        if level == 'academician':
            histories = histories.filter(count__gte=100)
        elif level == 'doctor':
            histories = histories.filter(count__gte=10, count__lt=100)
        elif level == 'master':
            histories = histories.filter(count__gte=3, count__lt=10)
        elif level == 'undergraduate':
            histories = histories.filter(count__gte=1, count__lt=3)

    # 排序
    ordering = request.query_params.get('ordering', '-count')
    if ordering in ['count', '-count', 'last_tried_at', '-last_tried_at']:
        histories = histories.order_by(ordering)

    # 分页
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    paged_histories = histories[start:end]

    serializer = UserDishHistoryListSerializer(paged_histories, many=True)
    return Response({
        'code': 200,
        'message': '获取历史记录成功',
        'data': {
            'histories': serializer.data,
            'total': histories.count(),
            'page': page,
            'page_size': page_size
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_dish_stats(request):
    """
    获取用户的菜品打卡统计信息
    包括各级别菜品数量、总打卡次数等
    """
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    histories = UserDishHistory.objects.filter(user=user)

    # 统计各级别菜品数量
    total_dishes = histories.count()
    total_check_ins = histories.aggregate(total=Count('count'))['total'] or 0

    # 计算实际的打卡总次数（所有count的和）
    total_check_ins_sum = sum(h.count for h in histories)

    academician_count = histories.filter(count__gte=100).count()
    doctor_count = histories.filter(count__gte=10, count__lt=100).count()
    master_count = histories.filter(count__gte=3, count__lt=10).count()
    undergraduate_count = histories.filter(count__gte=1, count__lt=3).count()

    # 获取最爱的菜品（打卡次数最多的前5个）
    favorite_dishes = histories.order_by('-count')[:5]
    favorite_dishes_data = UserDishHistoryListSerializer(favorite_dishes, many=True).data

    # 最近打卡的菜品
    recent_dishes = histories.order_by('-last_tried_at')[:5]
    recent_dishes_data = UserDishHistoryListSerializer(recent_dishes, many=True).data

    return Response({
        'code': 200,
        'message': '获取统计信息成功',
        'data': {
            'total_dishes': total_dishes,
            'total_check_ins': total_check_ins_sum,
            'level_distribution': {
                'academician': academician_count,
                'doctor': doctor_count,
                'master': master_count,
                'undergraduate': undergraduate_count
            },
            'favorite_dishes': favorite_dishes_data,
            'recent_dishes': recent_dishes_data
        }
    })


# ==================== 美食日历 ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_food_calendar(request):
    """
    获取用户的美食日历数据
    返回指定月份每天吃过的菜品
    """
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    # 获取年月参数（默认当前月）
    from datetime import datetime, timedelta
    import calendar as cal

    year = int(request.query_params.get('year', datetime.now().year))
    month = int(request.query_params.get('month', datetime.now().month))

    # 计算月份的第一天和最后一天
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, cal.monthrange(year, month)[1], 23, 59, 59)

    # 获取该月的所有打卡记录
    records = DishCheckInRecord.objects.filter(
        user=user,
        checked_in_at__gte=first_day,
        checked_in_at__lte=last_day
    ).select_related('dish').order_by('checked_in_at')

    # 按日期分组
    calendar_data = {}
    for record in records:
        date_str = record.date.strftime('%Y-%m-%d')

        if date_str not in calendar_data:
            calendar_data[date_str] = {
                'date': date_str,
                'dishes': [],
                'count': 0
            }

        calendar_data[date_str]['dishes'].append({
            'id': record.dish.id,
            'name': record.dish.name,
            'image': request.build_absolute_uri(record.dish.image.url) if record.dish.image else None,
            'canteen_name': record.dish.canteen.name,
            'checked_in_at': record.checked_in_at.strftime('%H:%M'),
            'notes': record.notes
        })
        calendar_data[date_str]['count'] += 1

    # 转换为列表并排序
    calendar_list = list(calendar_data.values())
    calendar_list.sort(key=lambda x: x['date'])

    return Response({
        'code': 200,
        'message': '获取美食日历成功',
        'data': {
            'year': year,
            'month': month,
            'calendar': calendar_list,
            'total_days': len(calendar_list),
            'total_check_ins': sum(day['count'] for day in calendar_list)
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_day_dishes(request):
    """
    获取指定日期吃过的菜品详情
    """
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

    # 获取日期参数
    from datetime import datetime
    date_str = request.query_params.get('date')  # 格式：YYYY-MM-DD

    if not date_str:
        return Response({
            'code': 400,
            'message': '请提供日期参数（格式：YYYY-MM-DD）',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({
            'code': 400,
            'message': '日期格式错误，应为：YYYY-MM-DD',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取该日期的所有打卡记录
    records = DishCheckInRecord.objects.filter(
        user=user,
        checked_in_at__date=target_date
    ).select_related('dish', 'dish__canteen').order_by('checked_in_at')

    # 序列化返回
    dishes_data = []
    for record in records:
        dishes_data.append({
            'id': record.id,
            'dish': {
                'id': record.dish.id,
                'name': record.dish.name,
                'image': request.build_absolute_uri(record.dish.image.url) if record.dish.image else None,
                'price': str(record.dish.price),
                'canteen_name': record.dish.canteen.name,
                'rating': str(record.dish.rating)
            },
            'checked_in_at': record.checked_in_at,
            'time': record.checked_in_at.strftime('%H:%M'),
            'notes': record.notes
        })

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'date': date_str,
            'dishes': dishes_data,
            'count': len(dishes_data)
        }
    })


# ==================== 用户成就系统 ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_achievements(request):
    """
    获取用户的成就列表
    包括学术成就、探索成就、打卡成就等
    """
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    from datetime import datetime, timedelta
    from django.db.models import Count, Q

    histories = UserDishHistory.objects.filter(user=user)
    check_in_records = DishCheckInRecord.objects.filter(user=user)

    # 统计数据
    total_dishes = histories.count()
    total_check_ins = sum(h.count for h in histories)
    academician_count = histories.filter(count__gte=100).count()
    doctor_count = histories.filter(count__gte=10, count__lt=100).count()
    master_count = histories.filter(count__gte=3, count__lt=10).count()
    undergraduate_count = histories.filter(count__gte=1, count__lt=3).count()

    # 不同食堂数量
    unique_canteens = Dish.objects.filter(
        id__in=histories.values_list('dish_id', flat=True)
    ).values('canteen').distinct().count()

    # 不同标签数量
    unique_tags = Tag.objects.filter(
        dishes__id__in=histories.values_list('dish_id', flat=True)
    ).distinct().count()

    # 连续打卡天数（最长记录）
    def calculate_max_streak():
        if not check_in_records.exists():
            return 0

        dates = set()
        for record in check_in_records:
            dates.add(record.date)

        if not dates:
            return 0

        sorted_dates = sorted(dates)
        max_streak = 1
        current_streak = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        return max_streak

    max_streak_days = calculate_max_streak()

    # 当前连续打卡天数
    def calculate_current_streak():
        if not check_in_records.exists():
            return 0

        today = datetime.now().date()
        current_streak = 0
        check_date = today

        while True:
            if check_in_records.filter(checked_in_at__date=check_date).exists():
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return current_streak

    current_streak_days = calculate_current_streak()

    # 定义成就列表
    achievements = []

    # ==================== 学术成就 ====================
    academic_achievements = {
        'category': 'academic',
        'category_name': '学术成就',
        'icon': '🎓',
        'achievements': []
    }

    # 本科生
    if undergraduate_count > 0:
        academic_achievements['achievements'].append({
            'id': 'undergraduate_1',
            'name': '入门学者',
            'description': f'获得 {undergraduate_count} 个本科称号',
            'icon': '🎓',
            'level': 'undergraduate',
            'unlocked': True,
            'progress': undergraduate_count,
            'requirement': undergraduate_count
        })

    # 硕士
    if master_count >= 1:
        academic_achievements['achievements'].append({
            'id': 'master_1',
            'name': '进阶学者',
            'description': f'获得 {master_count} 个硕士称号',
            'icon': '🎓',
            'level': 'master',
            'unlocked': True,
            'progress': master_count,
            'requirement': master_count
        })

    if master_count >= 5:
        academic_achievements['achievements'].append({
            'id': 'master_5',
            'name': '硕士导师',
            'description': '获得 5 个硕士称号',
            'icon': '🎓',
            'level': 'master',
            'unlocked': True,
            'progress': master_count,
            'requirement': 5
        })
    elif master_count > 0:
        academic_achievements['achievements'].append({
            'id': 'master_5',
            'name': '硕士导师',
            'description': '获得 5 个硕士称号',
            'icon': '🎓',
            'level': 'master',
            'unlocked': False,
            'progress': master_count,
            'requirement': 5
        })

    # 博士
    if doctor_count >= 1:
        academic_achievements['achievements'].append({
            'id': 'doctor_1',
            'name': '博学之士',
            'description': f'获得 {doctor_count} 个博士称号',
            'icon': '🎓',
            'level': 'doctor',
            'unlocked': True,
            'progress': doctor_count,
            'requirement': doctor_count
        })

    if doctor_count >= 3:
        academic_achievements['achievements'].append({
            'id': 'doctor_3',
            'name': '博士导师',
            'description': '获得 3 个博士称号',
            'icon': '🎓',
            'level': 'doctor',
            'unlocked': True,
            'progress': doctor_count,
            'requirement': 3
        })
    elif doctor_count > 0:
        academic_achievements['achievements'].append({
            'id': 'doctor_3',
            'name': '博士导师',
            'description': '获得 3 个博士称号',
            'icon': '🎓',
            'level': 'doctor',
            'unlocked': False,
            'progress': doctor_count,
            'requirement': 3
        })

    # 院士
    if academician_count >= 1:
        academic_achievements['achievements'].append({
            'id': 'academician_1',
            'name': '学术泰斗',
            'description': f'获得 {academician_count} 个院士称号',
            'icon': '🏆',
            'level': 'academician',
            'unlocked': True,
            'progress': academician_count,
            'requirement': academician_count
        })

    if academician_count >= 5:
        academic_achievements['achievements'].append({
            'id': 'academician_5',
            'name': '美食院士',
            'description': '获得 5 个院士称号',
            'icon': '🏆',
            'level': 'academician',
            'unlocked': True,
            'progress': academician_count,
            'requirement': 5
        })

    achievements.append(academic_achievements)

    # ==================== 探索成就 ====================
    exploration_achievements = {
        'category': 'exploration',
        'category_name': '探索成就',
        'icon': '🗺️',
        'achievements': []
    }

    # 菜品数量
    dish_milestones = [1, 5, 10, 20, 50, 100]
    dish_names = ['初尝美食', '美食爱好者', '美食达人', '美食专家', '美食大师', '美食鉴赏家']

    for i, milestone in enumerate(dish_milestones):
        if total_dishes >= milestone:
            exploration_achievements['achievements'].append({
                'id': f'dishes_{milestone}',
                'name': dish_names[i],
                'description': f'品尝过 {milestone} 种不同的菜品',
                'icon': '🍽️',
                'unlocked': True,
                'progress': total_dishes,
                'requirement': milestone
            })
        elif total_dishes > 0 and i > 0 and total_dishes >= dish_milestones[i-1]:
            exploration_achievements['achievements'].append({
                'id': f'dishes_{milestone}',
                'name': dish_names[i],
                'description': f'品尝过 {milestone} 种不同的菜品',
                'icon': '🍽️',
                'unlocked': False,
                'progress': total_dishes,
                'requirement': milestone
            })

    # 食堂探索
    canteen_milestones = [1, 3, 5]
    canteen_names = ['食堂探险者', '食堂游侠', '食堂大师']

    for i, milestone in enumerate(canteen_milestones):
        if unique_canteens >= milestone:
            exploration_achievements['achievements'].append({
                'id': f'canteens_{milestone}',
                'name': canteen_names[i],
                'description': f'在 {milestone} 个不同的食堂打过卡',
                'icon': '🏢',
                'unlocked': True,
                'progress': unique_canteens,
                'requirement': milestone
            })

    achievements.append(exploration_achievements)

    # ==================== 打卡成就 ====================
    checkin_achievements = {
        'category': 'checkin',
        'category_name': '打卡成就',
        'icon': '✅',
        'achievements': []
    }

    # 总打卡次数
    checkin_milestones = [1, 10, 50, 100, 500, 1000]
    checkin_names = ['打卡新手', '打卡达人', '打卡专家', '打卡大师', '打卡宗师', '打卡传说']

    for i, milestone in enumerate(checkin_milestones):
        if total_check_ins >= milestone:
            checkin_achievements['achievements'].append({
                'id': f'checkins_{milestone}',
                'name': checkin_names[i],
                'description': f'累计打卡 {milestone} 次',
                'icon': '✅',
                'unlocked': True,
                'progress': total_check_ins,
                'requirement': milestone
            })
        elif total_check_ins > 0 and i > 0 and total_check_ins >= checkin_milestones[i-1]:
            checkin_achievements['achievements'].append({
                'id': f'checkins_{milestone}',
                'name': checkin_names[i],
                'description': f'累计打卡 {milestone} 次',
                'icon': '✅',
                'unlocked': False,
                'progress': total_check_ins,
                'requirement': milestone
            })

    # 连续打卡
    streak_milestones = [3, 7, 14, 30, 100]
    streak_names = ['三天坚持', '一周达人', '两周坚持', '月度冠军', '百日打卡']

    for i, milestone in enumerate(streak_milestones):
        if max_streak_days >= milestone:
            checkin_achievements['achievements'].append({
                'id': f'streak_{milestone}',
                'name': streak_names[i],
                'description': f'连续打卡 {milestone} 天',
                'icon': '🔥',
                'unlocked': True,
                'progress': max_streak_days,
                'requirement': milestone
            })

    achievements.append(checkin_achievements)

    # 统计已解锁和总数
    total_unlocked = sum(
        len([a for a in cat['achievements'] if a['unlocked']])
        for cat in achievements
    )
    total_achievements = sum(len(cat['achievements']) for cat in achievements)

    return Response({
        'code': 200,
        'message': '获取成就列表成功',
        'data': {
            'achievements': achievements,
            'summary': {
                'total_unlocked': total_unlocked,
                'total_achievements': total_achievements,
                'unlock_rate': round(total_unlocked / total_achievements * 100, 1) if total_achievements > 0 else 0,
                'current_streak': current_streak_days,
                'max_streak': max_streak_days
            }
        }
    })
