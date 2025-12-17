"""
用户个人资料视图
"""
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q

from utils.jwt import encrypt_password, login_required

from .controllers import get_user_stats, update_user_password, update_user_profile
from .serializers import (
    UpdatePasswordSerializer,
    UpdateProfileSerializer,
    UserProfileSerializer,
    UserStatsSerializer,
    UserPreferenceTagsSerializer,
    CheckInDateSerializer,
    CheckInHistorySummarySerializer,
    PendingContentSerializer,
    AuditActionSerializer,
)
from list.models import Tag, Dish, Canteen, DishCheckInRecord, UserDishHistory
from list.serializers import TagSerializer, DishListSerializer, CanteenSerializer
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import math


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取个人资料成功",
            response={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "用户ID"},
                    "username": {"type": "string", "description": "用户名"},
                    "nickname": {"type": "string", "description": "用户昵称"},
                    "avatar": {"type": "string", "description": "头像URL"},
                    "created": {
                        "type": "string",
                        "format": "date-time",
                        "description": "创建时间",
                    },
                    "updated": {
                        "type": "string",
                        "format": "date-time",
                        "description": "更新时间",
                    },
                },
            },
        ),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户的个人资料",
    summary="获取个人资料",
    operation_id="get_profile",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_profile(request):
    """
    获取当前登录用户的个人资料
    """
    user = request.user
    serializer = UserProfileSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "nickname": {"type": "string", "description": "用户昵称（可选）"},
                "avatar": {
                    "type": "string",
                    "format": "binary",
                    "description": "头像图片文件（可选）",
                },
            },
        }
    },
    responses={
        200: OpenApiResponse(
            description="更新个人资料成功",
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "成功消息"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "用户ID"},
                            "username": {"type": "string", "description": "用户名"},
                            "nickname": {"type": "string", "description": "用户昵称"},
                            "avatar": {"type": "string", "description": "头像URL"},
                            "updated": {
                                "type": "string",
                                "format": "date-time",
                                "description": "更新时间",
                            },
                        },
                    },
                },
            },
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="更新当前登录用户的个人资料（昵称、头像）",
    summary="更新个人资料",
    operation_id="update_profile",
    tags=["Profile"],
)
@api_view(["PUT", "PATCH"])
@login_required
def update_profile(request):
    """
    更新当前登录用户的个人资料
    支持更新昵称和头像
    """
    user = request.user
    serializer = UpdateProfileSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"message": "参数错误", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    nickname = serializer.validated_data.get("nickname")
    avatar = request.FILES.get("avatar")

    # 至少需要更新一个字段
    if nickname is None and avatar is None:
        return Response(
            {"message": "至少需要提供一个更新字段"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    success, message = update_user_profile(user, nickname=nickname, avatar=avatar)

    if success:
        user.refresh_from_db()
        response_serializer = UserProfileSerializer(user, context={'request': request})
        return Response(
            {"message": message, "data": response_serializer.data},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"message": f"更新失败: {message}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "old_password": {"type": "string", "description": "旧密码"},
                "new_password": {"type": "string", "description": "新密码"},
                "confirm_password": {"type": "string", "description": "确认新密码"},
            },
            "required": ["old_password", "new_password", "confirm_password"],
        }
    },
    responses={
        200: OpenApiResponse(
            description="密码修改成功",
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "成功消息"},
                },
            },
        ),
        400: OpenApiResponse(description="参数错误或旧密码错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="修改当前登录用户的密码，需要验证旧密码",
    summary="修改密码",
    operation_id="update_password",
    tags=["Profile"],
)
@api_view(["POST"])
@login_required
def update_password(request):
    """
    修改当前登录用户的密码
    需要验证旧密码，并确认两次新密码输入一致
    """
    user = request.user
    serializer = UpdatePasswordSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"message": "参数错误", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_password = serializer.validated_data.get("old_password")
    new_password = serializer.validated_data.get("new_password")

    # 验证旧密码
    encrypted_old_password = encrypt_password(old_password)
    if user.password != encrypted_old_password:
        return Response(
            {"message": "旧密码错误"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 更新密码
    encrypted_new_password = encrypt_password(new_password)
    success, message = update_user_password(user, encrypted_new_password)

    if success:
        return Response({"message": message}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": f"密码修改失败: {message}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取统计信息成功",
            response={
                "type": "object",
                "properties": {
                    "liked_posts_count": {
                        "type": "integer",
                        "description": "点赞的帖子数量",
                    },
                    "commented_posts_count": {
                        "type": "integer",
                        "description": "评论的帖子数量",
                    },
                    "following_count": {
                        "type": "integer",
                        "description": "关注的人数量",
                    },
                },
            },
        ),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户的统计信息（点赞数、评论数、关注数）",
    summary="获取用户统计信息",
    operation_id="get_user_stats",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_stats(request):
    """
    获取当前登录用户的统计信息
    返回点赞的帖子数量、评论的帖子数量、关注的人数量
    """
    user = request.user
    stats = get_user_stats(user)
    serializer = UserStatsSerializer(data=stats)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 11/3 yyf 用户发布的帖子
@extend_schema(
    parameters=[
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={
        200: OpenApiResponse(description="获取用户帖子成功"),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户发布的帖子列表",
    summary="获取我的帖子",
    operation_id="get_my_posts",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_my_posts(request):
    """
    获取当前登录用户发布的帖子列表
    """
    from post.controllers import get_user_posts
    from post.serializers import PostSerializer

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    result = get_user_posts(request.user.id, page=page, page_size=page_size)

    serializer = PostSerializer(result['posts'], many=True, context={'request': request})

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'posts': serializer.data,
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages']
            }
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: OpenApiResponse(description="获取最近3个帖子成功"),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户最近发布的3个帖子",
    summary="获取最近3个帖子",
    operation_id="get_recent_posts",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_recent_posts(request):
    """
    获取当前登录用户最近发布的3个帖子
    """
    from post.controllers import get_user_recent_posts
    from post.serializers import PostSummarySerializer

    posts = get_user_recent_posts(request.user.id, limit=3)
    serializer = PostSummarySerializer(posts, many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


# ==================== 内容审核视图 ====================

@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取待审核内容列表成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "获取成功"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "pending_contents": {"type": "array"},
                            "total": {"type": "integer"}
                        }
                    }
                }
            }
        ),
        403: OpenApiResponse(description="权限不足"),
    },
    description="获取所有待审核的内容（管理员功能）",
    summary="获取待审核内容",
    tags=["Audit"],
)
@api_view(['GET'])
@login_required
def get_pending_contents(request):
    """
    获取所有待审核的内容
    仅管理员可访问
    """
    user = request.user

    # 检查是否为管理员
    if not (user.is_staff or user.is_superuser):
        return Response({
            'code': 403,
            'message': '权限不足，仅管理员可访问'
        }, status=status.HTTP_403_FORBIDDEN)

    pending_contents = []

    # 获取待审核的帖子
    from post.models import Post
    pending_posts = Post.objects.filter(status='pending').select_related('author', 'dish')
    for post in pending_posts:
        pending_contents.append({
            'id': post.id,
            'type': 'post',
            'title': post.subject,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at,
            'images': post.images,
        })

    # 获取待审核的评论
    from post.models import Comment
    pending_comments = Comment.objects.filter(status='pending').select_related('author', 'post')
    for comment in pending_comments:
        pending_contents.append({
            'id': comment.id,
            'type': 'comment',
            'title': f'回复: {comment.post.subject}',
            'content': comment.content,
            'author': comment.author.username,
            'created_at': comment.created_at,
            'images': comment.images,
        })

    # 获取待审核的菜品评论
    from list.models import Review
    pending_reviews = Review.objects.filter(status='pending').select_related('user', 'dish')
    for review in pending_reviews:
        pending_contents.append({
            'id': review.id,
            'type': 'review',
            'title': f'评价: {review.dish.name}',
            'content': review.content,
            'author': review.user.username,
            'created_at': review.created_at,
            'images': review.images,
        })

    # 获取待审核的标签
    from list.models import Dish
    pending_tags = Dish.objects.filter(pending_tags__isnull=False).distinct()
    for dish in pending_tags:
        pending_tag_objects = dish.pending_tags.all()
        for tag in pending_tag_objects:
            pending_contents.append({
                'id': f"{dish.id}_{tag.id}",
                'type': 'tag',
                'title': f'标签: {tag.name}',
                'content': f'用户为菜品"{dish.name}"添加标签"{tag.name}"',
                'author': '用户',  # 标签添加者信息可能需要额外存储
                'created_at': dish.created_at,
                'images': [],
            })

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'pending_contents': pending_contents,
            'total': len(pending_contents)
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=AuditActionSerializer,
    responses={
        200: OpenApiResponse(description="审核操作成功"),
        400: OpenApiResponse(description="参数错误"),
        403: OpenApiResponse(description="权限不足"),
        404: OpenApiResponse(description="内容不存在"),
    },
    description="审核指定内容（管理员功能）",
    summary="审核内容",
    tags=["Audit"],
)
@api_view(['POST'])
@login_required
def audit_content(request, content_type, content_id):
    """
    审核指定内容
    URL: /api/v1/profile/audit/{content_type}/{content_id}/
    content_type: post/comment/review/tag
    """
    user = request.user

    # 检查是否为管理员
    if not (user.is_staff or user.is_superuser):
        return Response({
            'code': 403,
            'message': '权限不足，仅管理员可访问'
        }, status=status.HTTP_403_FORBIDDEN)

    # 验证请求数据
    serializer = AuditActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    action = serializer.validated_data['action']
    reason = serializer.validated_data.get('reason', '')

    from django.utils import timezone

    try:
        # 根据内容类型处理审核
        if content_type == 'post':
            from post.models import Post
            content_obj = Post.objects.get(id=content_id, status='pending')

        elif content_type == 'comment':
            from post.models import Comment
            content_obj = Comment.objects.get(id=content_id, status='pending')

        elif content_type == 'review':
            from list.models import Review
            content_obj = Review.objects.get(id=content_id, status='pending')

        elif content_type == 'tag':
            # 标签审核比较特殊，需要解析 dish_id 和 tag_id
            try:
                dish_id, tag_id = content_id.split('_')
                dish_id = int(dish_id)
                tag_id = int(tag_id)
            except ValueError:
                return Response({
                    'code': 400,
                    'message': '无效的标签ID格式'
                }, status=status.HTTP_400_BAD_REQUEST)

            from list.models import Dish, Tag
            dish = Dish.objects.get(id=dish_id)
            tag = Tag.objects.get(id=tag_id)

            if action == 'approve':
                # 批准标签：从 pending_tags 移到 tags
                if tag in dish.pending_tags.all() and tag not in dish.tags.all():
                    dish.tags.add(tag)
                dish.pending_tags.remove(tag)
                message = f'标签"{tag.name}"审核通过'
            else:
                # 拒绝标签：从 pending_tags 中移除
                dish.pending_tags.remove(tag)
                message = f'标签"{tag.name}"审核拒绝'

            return Response({
                'code': 200,
                'message': message
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'code': 400,
                'message': '不支持的内容类型'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 处理帖子、评论、评价的审核
        if action == 'approve':
            content_obj.status = 'approved'
            content_obj.audit_reason = ''
            message = '内容审核通过'
        else:
            content_obj.status = 'rejected'
            content_obj.audit_reason = reason
            message = f'内容审核拒绝: {reason}'

        content_obj.audited_at = timezone.now()
        content_obj.save()

        return Response({
            'code': 200,
            'message': message
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'code': 404,
            'message': '内容不存在或已审核'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    parameters=[
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={
        200: OpenApiResponse(description="获取点赞帖子列表成功"),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户点赞过的所有帖子",
    summary="获取点赞的帖子",
    operation_id="get_liked_posts",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_liked_posts(request):
    """
    获取当前登录用户点赞过的所有帖子
    """
    from post.controllers import get_user_liked_posts
    from post.serializers import PostSummarySerializer

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    result = get_user_liked_posts(request.user.id, page=page, page_size=page_size)

    serializer = PostSummarySerializer(result['posts'], many=True)

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'posts': serializer.data,
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages']
            }
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={
        200: OpenApiResponse(description="获取评论列表成功"),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户发出的所有评论",
    summary="获取我的评论",
    operation_id="get_my_comments",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_my_comments(request):
    """
    获取当前登录用户发出的所有评论
    """
    from post.controllers import get_user_comments

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    result = get_user_comments(request.user.id, page=page, page_size=page_size)

    # 构建评论数据
    comments_data = []
    for comment in result['comments']:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at,
            'post_id': comment.post.id,
            'post_subject': comment.post.subject
        })

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'comments': comments_data,
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages']
            }
        }
    }, status=status.HTTP_200_OK)


# ==================== 用户偏好标签管理 ====================

@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取偏好标签成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "获取偏好标签成功"},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "dish_count": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        ),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户的偏好标签列表",
    summary="获取用户偏好标签",
    operation_id="get_preference_tags",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_preference_tags(request):
    """
    获取当前登录用户的偏好标签列表
    """
    user = request.user
    tags = user.preference_tags.all()
    serializer = TagSerializer(tags, many=True)

    return Response({
        'code': 200,
        'message': '获取偏好标签成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "tag_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "标签ID列表"
                }
            },
            "required": ["tag_ids"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="设置偏好标签成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "偏好标签设置成功"},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"}
                            }
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="设置或更新当前登录用户的偏好标签（会覆盖原有标签）",
    summary="设置用户偏好标签",
    operation_id="set_preference_tags",
    tags=["Profile"],
)
@api_view(["POST", "PUT"])
@login_required
def set_preference_tags(request):
    """
    设置或更新当前登录用户的偏好标签
    会覆盖用户原有的所有偏好标签
    """
    user = request.user
    serializer = UserPreferenceTagsSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    tag_ids = serializer.validated_data.get('tag_ids')

    # 获取标签对象
    tags = Tag.objects.filter(id__in=tag_ids)

    # 设置用户偏好标签（覆盖原有）
    user.preference_tags.set(tags)

    # 返回更新后的标签列表
    updated_tags = user.preference_tags.all()
    result_serializer = TagSerializer(updated_tags, many=True)

    return Response({
        'code': 200,
        'message': '偏好标签设置成功',
        'data': result_serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "tag_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "要添加的标签ID列表"
                }
            },
            "required": ["tag_ids"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="添加偏好标签成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "偏好标签添加成功"}
                }
            }
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="向用户偏好标签列表中添加新标签（不覆盖原有标签）",
    summary="添加偏好标签",
    operation_id="add_preference_tags",
    tags=["Profile"],
)
@api_view(["POST"])
@login_required
def add_preference_tags(request):
    """
    向用户偏好标签列表中添加新标签（不覆盖原有标签）
    """
    user = request.user
    serializer = UserPreferenceTagsSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    tag_ids = serializer.validated_data.get('tag_ids')

    # 获取标签对象
    tags = Tag.objects.filter(id__in=tag_ids)

    # 添加新标签（不覆盖已有）
    user.preference_tags.add(*tags)

    # 返回更新后的标签列表
    updated_tags = user.preference_tags.all()
    result_serializer = TagSerializer(updated_tags, many=True)

    return Response({
        'code': 200,
        'message': '偏好标签添加成功',
        'data': result_serializer.data
    }, status=status.HTTP_200_OK)


# ==================== 个性化推荐 ====================

@extend_schema(
    parameters=[
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={
        200: OpenApiResponse(
            description="获取推荐菜品成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "获取推荐菜品成功"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "dishes": {"type": "array"},
                            "total": {"type": "integer"},
                            "user_tags": {"type": "array"}
                        }
                    }
                }
            }
        ),
        401: OpenApiResponse(description="未登录"),
        404: OpenApiResponse(description="用户未设置偏好标签"),
    },
    description="根据用户偏好标签 + 热度(view_count) + 评分 推荐菜品，按热度和匹配度排序",
    summary="获取个性化推荐菜品（按热度）",
    operation_id="get_recommended_dishes",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_recommended_dishes(request):
    """
    根据用户偏好标签 + 热度(view_count) + 评分 综合推荐菜品
    推荐逻辑：
    1. 匹配用户偏好标签的菜品
    2. 优先级：标签匹配度 > 评分 > 热度(view_count)
    """
    user = request.user

    # 获取用户偏好标签
    user_tags = user.preference_tags.all()

    if not user_tags.exists():
        return Response({
            'code': 404,
            'message': '用户未设置偏好标签，请先设置偏好标签',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    # 获取分页参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    # 查询包含用户偏好标签的菜品
    dishes = Dish.objects.filter(
        tags__in=user_tags
    ).annotate(
        matched_tags_count=Count('tags', filter=Q(tags__in=user_tags))
    ).distinct().select_related('canteen')

    # 按标签匹配度 + 评分 + 热度排序
    dishes = dishes.order_by('-matched_tags_count', '-rating', '-view_count')

    # 分页
    total = dishes.count()
    start = (page - 1) * page_size
    end = start + page_size
    dishes = dishes[start:end]

    # 序列化
    dish_serializer = DishListSerializer(dishes, many=True)
    tag_serializer = TagSerializer(user_tags, many=True)

    return Response({
        'code': 200,
        'message': '获取推荐菜品成功',
        'data': {
            'dishes': dish_serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'user_tags': tag_serializer.data
        }
    }, status=status.HTTP_200_OK)


# ==================== 美食日历相关视图 ====================

def _get_or_create_auth_user(request):
    """将自定义登录用户统一映射到 Django 内置 AuthUser"""
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


def _calculate_achievement_tier(check_in_count):
    """计算成就等级"""
    if check_in_count >= 11:
        return 'rainbow'
    elif check_in_count >= 6:
        return 'gold'
    elif check_in_count >= 3:
        return 'silver'
    elif check_in_count >= 1:
        return 'bronze'
    else:
        return None


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='开始日期，格式 YYYY-MM-DD，默认为当前日期前6天',
            required=False,
        ),
        OpenApiParameter(
            name='end_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='结束日期，格式 YYYY-MM-DD，默认为当前日期',
            required=False,
        ),
        OpenApiParameter(
            name='year',
            type=int,
            location=OpenApiParameter.QUERY,
            description='年份，用于按月查询',
            required=False,
        ),
        OpenApiParameter(
            name='month',
            type=int,
            location=OpenApiParameter.QUERY,
            description='月份（1-12），用于按月查询',
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(description='获取成功'),
        401: OpenApiResponse(description='未授权，请先登录'),
        400: OpenApiResponse(description='日期格式错误'),
    },
    description='获取用户打卡历史（按日期范围或月份）',
    summary='获取打卡历史',
    tags=['Profile'],
)
@api_view(['GET'])
@login_required
def get_check_in_history(request):
    """
    获取用户打卡历史（按日期范围或月份）
    """
    # 获取用户
    auth_user = _get_or_create_auth_user(request)
    if not auth_user:
        return Response({
            'code': 401,
            'message': '未授权，请先登录'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # 解析日期参数
    try:
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)

        # 按月查询
        if year and month:
            if not (1 <= int(month) <= 12):
                return Response({
                    'code': 400,
                    'message': '月份必须在1-12之间'
                }, status=status.HTTP_400_BAD_REQUEST)

            start_date = datetime(int(year), int(month), 1).date()
            # 计算该月最后一天
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date() - timedelta(days=1)
        # 按日期范围查询
        elif start_date_str or end_date_str:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                # 默认当前日期前6天
                start_date = timezone.now().date() - timedelta(days=6)

            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                # 默认当前日期
                end_date = timezone.now().date()
        else:
            # 默认最近7天
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)

        if start_date > end_date:
            return Response({
                'code': 400,
                'message': '开始日期不能晚于结束日期'
            }, status=status.HTTP_400_BAD_REQUEST)

    except ValueError as e:
        return Response({
            'code': 400,
            'message': f'日期格式错误: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 查询打卡记录
    check_in_records = DishCheckInRecord.objects.filter(
        user=auth_user,
        checked_in_at__date__gte=start_date,
        checked_in_at__date__lte=end_date
    ).select_related('dish', 'dish__canteen', 'dish__window').prefetch_related('dish__tags').order_by('-checked_in_at')

    # 获取用户菜品历史（用于统计）
    dish_history_map = {}
    dish_histories = UserDishHistory.objects.filter(user=auth_user).select_related('dish')
    for history in dish_histories:
        dish_history_map[history.dish_id] = history

    # 按日期分组
    check_ins_by_date = defaultdict(list)
    total_check_ins = 0
    unique_dishes = set()
    total_consumption = Decimal('0.00')
    dish_frequency = defaultdict(int)

    for record in check_in_records:
        date_str = record.checked_in_at.date().isoformat()
        dish = record.dish

        # 获取历史统计
        history = dish_history_map.get(dish.id)
        check_in_count = history.count if history else 0
        total_consumption_dish = (dish.price * check_in_count) if history else Decimal('0.00')

        # 计算成就等级
        achievement_tier = _calculate_achievement_tier(check_in_count)

        # 构建菜品数据
        dish_data = {
            'dish': dish,
            'check_in_time': record.checked_in_at,
            'check_in_count': check_in_count,
            'total_consumption': total_consumption_dish,
            'achievement_tier': achievement_tier,
        }

        check_ins_by_date[date_str].append(dish_data)
        total_check_ins += 1
        unique_dishes.add(dish.id)
        # 累计消费使用单次打卡的价格（因为这是本次打卡的消费）
        total_consumption += dish.price
        dish_frequency[dish.id] += 1

    # 构建响应数据
    check_ins_list = []
    current_date = start_date

    # 生成日期范围内的所有日期（包括没有打卡的日期）
    while current_date <= end_date:
        date_str = current_date.isoformat()
        dishes_for_date = check_ins_by_date.get(date_str, [])

        # 序列化菜品数据
        dishes_serialized = []
        for dish_data in dishes_for_date:
            dish = dish_data['dish']
            # 构建图片URL
            image_url = None
            if dish.image:
                image_url = dish.image.url
                # 如果是相对路径，确保以 /media/ 开头
                if not image_url.startswith('http'):
                    if not image_url.startswith('/'):
                        image_url = '/' + image_url

            dishes_serialized.append({
                'id': dish.id,
                'name': dish.name,
                'image': image_url,
                'canteen_name': dish.canteen.name if dish.canteen else '',
                'window_name': dish.window.name if dish.window else None,
                'price': float(dish.price),
                'rating': float(dish.rating),
                'check_in_time': dish_data['check_in_time'].isoformat(),
                'check_in_count': dish_data['check_in_count'],
                'total_consumption': float(dish_data['total_consumption']),
                'achievement_tier': dish_data['achievement_tier'],
                'tags': [{'id': tag.id, 'name': tag.name} for tag in dish.tags.all()],
            })

        check_ins_list.append({
            'date': date_str,
            'dishes': dishes_serialized
        })

        current_date += timedelta(days=1)

    # 计算统计摘要
    most_frequent_dish = None
    if dish_frequency:
        most_frequent_dish_id = max(dish_frequency.items(), key=lambda x: x[1])[0]
        most_frequent_dish_obj = Dish.objects.get(id=most_frequent_dish_id)
        most_frequent_dish = {
            'id': most_frequent_dish_obj.id,
            'name': most_frequent_dish_obj.name,
            'count': dish_frequency[most_frequent_dish_id]
        }

    summary = {
        'total_check_ins': total_check_ins,
        'total_dishes': len(unique_dishes),
        'total_consumption': float(total_consumption),
        'most_frequent_dish': most_frequent_dish
    }

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'check_ins': check_ins_list,
            'summary': summary
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='year',
            type=int,
            location=OpenApiParameter.QUERY,
            description='年份',
            required=True,
        ),
        OpenApiParameter(
            name='month',
            type=int,
            location=OpenApiParameter.QUERY,
            description='月份（1-12）',
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(description='获取成功'),
        401: OpenApiResponse(description='未授权，请先登录'),
        400: OpenApiResponse(description='参数错误'),
    },
    description='获取月度打卡概览（快速查看哪些日期有打卡）',
    summary='获取月度打卡概览',
    tags=['Profile'],
)
@api_view(['GET'])
@login_required
def get_check_in_calendar(request):
    """
    获取月度打卡概览（快速查看哪些日期有打卡）
    """
    # 获取用户
    auth_user = _get_or_create_auth_user(request)
    if not auth_user:
        return Response({
            'code': 401,
            'message': '未授权，请先登录'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # 获取参数
    try:
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))

        if not (1 <= month <= 12):
            return Response({
                'code': 400,
                'message': '月份必须在1-12之间'
            }, status=status.HTTP_400_BAD_REQUEST)

    except (ValueError, TypeError):
        return Response({
            'code': 400,
            'message': '年份和月份参数必需且必须为整数'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 计算月份的开始和结束日期
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

    # 查询该月的打卡记录，按日期分组统计
    check_in_records = DishCheckInRecord.objects.filter(
        user=auth_user,
        checked_in_at__date__gte=start_date,
        checked_in_at__date__lte=end_date
    ).values('checked_in_at__date').annotate(count=Count('id')).order_by('checked_in_at__date')

    # 构建响应数据
    check_in_dates = [
        {
            'date': record['checked_in_at__date'].isoformat(),
            'count': record['count']
        }
        for record in check_in_records
    ]

    return Response({
        'code': 200,
        'message': '获取成功',
        'data': {
            'year': year,
            'month': month,
            'check_in_dates': check_in_dates
        }
    }, status=status.HTTP_200_OK)
