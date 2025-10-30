from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q, Avg, Count
from .models import Canteen, Dish, Tag, Rating, Review
from .serializers import (
    CanteenSerializer, DishSerializer, DishListSerializer, TagSerializer,
    RatingSerializer, ReviewSerializer, ReviewListSerializer
)


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

    # 支持搜索
    search = request.query_params.get('search', None)
    if search:
        dishes = dishes.filter(Q(name__icontains=search) | Q(description__icontains=search))

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

    # 搜索
    search = request.query_params.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

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

    ratings=Rating.objects.filter(dish=dish).aggregate(Avg('rating'))['rating__avg']
    if ratings is None:
        ratings = 0.0
    else:
        ratings = float(ratings)

    # 简单的移动平均
    new_rating = (ratings * dish.view_count + rating_value) / (dish.view_count + 1)
    dish.rating = round(new_rating, 2)
    dish.save(update_fields=['rating'])
    Rating.objects.create(dish=dish, user=user, rating=rating_value)
    return Response({
        'code': 200,
        'message': '评分成功',
        'data': {
            'dish_id': dish.id,
            'new_rating': float(dish.rating)
        }
    })


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
    user = request.user

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
    支持排序：按时间(默认)、点赞数
    """
    dish = get_object_or_404(Dish, id=dish_id)
    reviews = Review.objects.filter(dish=dish)

    # 排序
    ordering = request.query_params.get('ordering', '-created_at')
    if ordering in ['created_at', '-created_at', 'likes_count', '-likes_count']:
        reviews = reviews.order_by(ordering)

    serializer = ReviewListSerializer(reviews, many=True)
    return Response({
        'code': 200,
        'message': '获取评论列表成功',
        'data': {
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
    user = request.user

    # 检查用户是否已经评论过
    existing_review = Review.objects.filter(user=user, dish=dish).first()
    if existing_review:
        return Response({
            'code': 400,
            'message': '您已经评论过该菜品，请编辑现有评论',
            'data': {'review_id': existing_review.id}
        }, status=status.HTTP_400_BAD_REQUEST)

    # 处理评分（如果提供）
    rating_score = request.data.get('rating_score')
    rating_obj = None

    if rating_score:
        try:
            rating_score = float(rating_score)
            if rating_score < 1.0 or rating_score > 5.0:
                return Response({
                    'code': 400,
                    'message': '评分必须在 1.0-5.0 之间'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 创建或更新评分
            rating_obj, created = Rating.objects.update_or_create(
                user=user,
                dish=dish,
                defaults={'score': rating_score}
            )

            # 重新计算菜品平均分
            avg_rating = Rating.objects.filter(dish=dish).aggregate(Avg('score'))['score__avg']
            dish.rating = round(avg_rating, 2) if avg_rating else 0
            dish.save(update_fields=['rating'])

        except ValueError:
            return Response({
                'code': 400,
                'message': '评分格式不正确'
            }, status=status.HTTP_400_BAD_REQUEST)

    # 创建评论
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        review = serializer.save(user=user, dish=dish, rating=rating_obj)

        return Response({
            'code': 201,
            'message': '评论创建成功',
            'data': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'code': 400,
        'message': '评论创建失败',
        'errors': serializer.errors
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

    # 检查权限：只能编辑自己的评论
    if review.user != request.user:
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

    # 检查权限：只能删除自己的评论，或者管理员
    if review.user != request.user and not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'code': 403,
            'message': '您没有权限删除此评论'
        }, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({
        'code': 200,
        'message': '评论删除成功'
    })
