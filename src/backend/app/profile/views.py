"""
用户个人资料视图
"""
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.jwt import encrypt_password, login_required

from .controllers import get_user_stats, update_user_password, update_user_profile
from .serializers import (
    UpdatePasswordSerializer,
    UpdateProfileSerializer,
    UserProfileSerializer,
    UserStatsSerializer,
)


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
