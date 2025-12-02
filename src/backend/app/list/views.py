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
from django.db.models import Q, Avg, Count
from .models import Canteen, Dish, Tag, Rating, Review, UserDishHistory
from django.contrib.auth.models import User as AuthUser
from .serializers import (
    CanteenSerializer, DishSerializer, DishListSerializer, TagSerializer,
    RatingSerializer, ReviewSerializer, ReviewListSerializer,
    UserDishHistorySerializer, UserDishHistoryListSerializer
)

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

    # 创建或更新用户对该菜品的评分（Rating表字段为 score，不是 rating）
    rating_obj, created = Rating.objects.update_or_create(dish=dish, user=auth_user, defaults={'score': rating_value})

    # 重新计算平均分，聚合字段应为 'score'
    avg_score = Rating.objects.filter(dish=dish).aggregate(avg=Avg('score'))['avg']
    dish.rating = round(float(avg_score), 2) if avg_score is not None else 0.0
    dish.save(update_fields=['rating'])

    return Response({
        'code': 200,
        'message': '评分成功' if created else '已更改评分',
        'data': {
            'dish_id': dish.id,
            'user_score': float(rating_obj.score),
            'new_rating': float(dish.rating)
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
    - 普通用户：标签添加到pending_tags（待审核）
    - 管理员：标签直接添加到tags

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

    # 处理现有标签
    if tag_ids:
        tags = Tag.objects.filter(id__in=tag_ids)

        if user.is_staff or user.is_superuser:
            # 管理员直接添加到tags
            for tag in tags:
                if tag not in dish.tags.all():
                    dish.tags.add(tag)
            message = '标签添加成功'
        else:
            # 普通用户添加到pending_tags
            for tag in tags:
                if tag not in dish.pending_tags.all():
                    dish.pending_tags.add(tag)
            message = '标签已提交，等待管理员审核'

    # 处理新标签
    if tag_name:
        # 检查标签是否已存在
        tag, created = Tag.objects.get_or_create(name=tag_name.strip())

        if user.is_staff or user.is_superuser:
            if tag not in dish.tags.all():
                dish.tags.add(tag)
            message = '标签添加成功'
        else:
            if tag not in dish.pending_tags.all():
                dish.pending_tags.add(tag)
            message = '标签已提交，等待管理员审核'

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

    # 创建评论
    # 若前端未传 images，设为空列表避免验证错误
    incoming_data = request.data.copy()
    if 'images' not in incoming_data or incoming_data.get('images') in [None, '']:
        incoming_data['images'] = []
    serializer = ReviewSerializer(data=incoming_data, context={'request': request})
    if serializer.is_valid():
        review = serializer.save(user=user, dish=dish, rating=rating_obj, published_score=rating_obj.score)

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
    if isinstance(request.user, AuthUser):
        user = request.user
    else:
        user = AuthUser.objects.filter(username=getattr(request.user, 'username', None)).first()
        if not user and getattr(request.user, 'username', None):
            user = AuthUser.objects.create(username=request.user.username)

    # 获取或创建历史记录
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
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_dish_history(request):
    """
    获取用户的菜品历史记录
    支持筛选和排序
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
