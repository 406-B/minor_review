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
    PendingContentSerializer,
    AuditActionSerializer,
)
from list.models import Tag, Dish, Canteen
from list.serializers import TagSerializer, DishListSerializer, CanteenSerializer
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


# ==================== 距离计算工具函数 ====================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    计算两点之间的距离（米）
    使用 Haversine 公式
    """
    R = 6371000  # 地球半径（米）

    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lon = math.radians(float(lon2) - float(lon1))

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ==================== 个性化推荐 ====================

@extend_schema(
    parameters=[
        OpenApiParameter(name='latitude', type=float, description='用户纬度（可选，提供后按距离优先排序）'),
        OpenApiParameter(name='longitude', type=float, description='用户经度（可选，提供后按距离优先排序）'),
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
    description="根据用户偏好标签和位置综合推荐菜品，优先推荐距离近且匹配偏好的菜品",
    summary="获取个性化推荐菜品",
    operation_id="get_recommended_dishes",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_recommended_dishes(request):
    """
    根据用户偏好标签和位置综合推荐菜品
    推荐逻辑：
    1. 匹配用户偏好标签的菜品
    2. 如果提供了位置信息，综合距离和偏好进行排序
    3. 排序优先级：距离近 + 标签匹配度高 + 评分高
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

    # 获取位置参数（可选）
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    has_location = latitude and longitude

    # 获取分页参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    # 查询包含用户偏好标签的菜品
    dishes = Dish.objects.filter(
        tags__in=user_tags
    ).annotate(
        matched_tags_count=Count('tags', filter=Q(tags__in=user_tags))
    ).distinct().select_related('canteen')

    # 如果有位置信息，计算距离并综合排序
    if has_location:
        try:
            lat = float(latitude)
            lon = float(longitude)

            # 获取菜品列表并计算距离
            dishes_list = list(dishes)
            dishes_with_score = []

            for dish in dishes_list:
                # 计算食堂距离
                if dish.canteen.latitude and dish.canteen.longitude:
                    distance = haversine_distance(
                        lat, lon,
                        float(dish.canteen.latitude),
                        float(dish.canteen.longitude)
                    )
                else:
                    distance = float('inf')  # 无位置信息的食堂放最后

                # 综合评分：距离越近分越高，标签匹配越多分越高，评分越高分越高
                # 距离分数：1000米内满分，超过1000米递减
                distance_score = max(0, 100 - (distance / 10))  # 每10米扣1分
                tag_score = dish.matched_tags_count * 20  # 每匹配一个标签加20分
                rating_score = float(dish.rating) * 10  # 评分 * 10

                total_score = distance_score + tag_score + rating_score

                dishes_with_score.append({
                    'dish': dish,
                    'distance': distance,
                    'total_score': total_score,
                    'matched_tags_count': dish.matched_tags_count
                })

            # 按综合评分排序
            dishes_with_score.sort(key=lambda x: -x['total_score'])

            # 分页
            total = len(dishes_with_score)
            start = (page - 1) * page_size
            end = start + page_size
            paged_dishes = dishes_with_score[start:end]

            # 构建返回数据（包含距离信息）
            dishes_data = []
            for item in paged_dishes:
                dish_data = DishListSerializer(item['dish']).data
                dish_data['distance'] = round(item['distance'], 2) if item['distance'] != float('inf') else None
                dish_data['matched_tags_count'] = item['matched_tags_count']
                dishes_data.append(dish_data)

            return Response({
                'code': 200,
                'message': '获取推荐菜品成功',
                'data': {
                    'dishes': dishes_data,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'user_tags': TagSerializer(user_tags, many=True).data,
                    'location_enabled': True
                }
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

        except ValueError:
            pass  # 位置参数格式错误，降级为无位置排序

    # 无位置信息时，按标签匹配度和评分排序
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
            'user_tags': tag_serializer.data,
            'location_enabled': False
        }
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


# ==================== 基于位置的推荐（仅最近食堂） ====================

@extend_schema(
    parameters=[
        OpenApiParameter(name='latitude', type=float, required=True, description='用户纬度'),
        OpenApiParameter(name='longitude', type=float, required=True, description='用户经度'),
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={
        200: OpenApiResponse(
            description="获取附近推荐菜品成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "example": 200},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        ),
        400: OpenApiResponse(description="缺少位置参数"),
        401: OpenApiResponse(description="未登录"),
    },
    description="根据用户位置和偏好标签推荐最近食堂的菜品",
    summary="获取附近推荐菜品",
    operation_id="get_nearby_recommended_dishes",
    tags=["Profile"],
)
@api_view(["GET"])
@login_required
def get_nearby_recommended_dishes(request):
    """
    根据用户位置和偏好标签推荐最近食堂的菜品
    推荐逻辑：
    1. 计算用户与各食堂的距离
    2. 找到最近的食堂
    3. 从最近食堂中筛选匹配用户偏好标签的菜品
    4. 按匹配度和评分排序
    """
    user = request.user

    # 获取位置参数
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    if not latitude or not longitude:
        return Response({
            'code': 400,
            'message': '请提供位置信息（latitude 和 longitude）',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response({
            'code': 400,
            'message': '位置参数格式不正确',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    # 获取分页参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    # 获取所有有位置信息的食堂
    canteens = Canteen.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

    if not canteens.exists():
        return Response({
            'code': 404,
            'message': '暂无食堂位置信息',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    # 计算距离并排序
    canteens_with_distance = []
    for canteen in canteens:
        distance = haversine_distance(
            latitude, longitude,
            canteen.latitude, canteen.longitude
        )
        canteen.distance = distance
        canteens_with_distance.append((canteen, distance))

    # 按距离排序
    canteens_with_distance.sort(key=lambda x: x[1])

    # 获取最近的食堂
    nearest_canteen, nearest_distance = canteens_with_distance[0]

    # 获取用户偏好标签
    user_tags = user.preference_tags.all()

    # 查询该食堂的菜品
    dishes = Dish.objects.filter(canteen=nearest_canteen)

    # 如果用户有偏好标签，优先推荐匹配的菜品
    if user_tags.exists():
        dishes = dishes.filter(tags__in=user_tags).annotate(
            matched_tags_count=Count('tags', filter=Q(tags__in=user_tags))
        ).distinct().order_by('-matched_tags_count', '-rating', '-view_count')
    else:
        dishes = dishes.order_by('-rating', '-view_count')

    # 分页
    total = dishes.count()
    start = (page - 1) * page_size
    end = start + page_size
    dishes = dishes[start:end]

    # 序列化
    dish_serializer = DishListSerializer(dishes, many=True)

    # 食堂信息
    canteen_data = {
        'id': nearest_canteen.id,
        'name': nearest_canteen.name,
        'address': nearest_canteen.address,
        'distance': round(nearest_distance, 2),
        'latitude': float(nearest_canteen.latitude),
        'longitude': float(nearest_canteen.longitude),
    }

    # 附近食堂列表（前5个）
    nearby_canteens = []
    for canteen, distance in canteens_with_distance[:5]:
        nearby_canteens.append({
            'id': canteen.id,
            'name': canteen.name,
            'address': canteen.address,
            'distance': round(distance, 2),
        })

    return Response({
        'code': 200,
        'message': '获取附近推荐菜品成功',
        'data': {
            'nearest_canteen': canteen_data,
            'nearby_canteens': nearby_canteens,
            'dishes': dish_serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'user_tags': TagSerializer(user_tags, many=True).data if user_tags.exists() else []
        }
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
