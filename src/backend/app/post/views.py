from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema, OpenApiParameter
from utils.jwt import login_required
from .serializers import (
    PostSerializer, PostDetailSerializer, CommentSerializer,
    CreatePostSerializer, CreateCommentSerializer, PostHomeSerializer
)
from . import controllers


@extend_schema(
    tags=['社区论坛'],
    summary='获取帖子列表',
    parameters=[
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={200: PostSerializer(many=True)}
)
@require_http_methods(["GET"])
def post_list(request):
    """获取帖子列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    result = controllers.get_post_list(page=page, page_size=page_size)
    
    serializer = PostSerializer(result['posts'], many=True, context={'request': request})
    
    return JsonResponse({
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
    })


@extend_schema(
    tags=['社区论坛'],
    summary='获取帖子详情',
    parameters=[
        OpenApiParameter(name='post_id', type=int, location=OpenApiParameter.PATH, description='帖子ID'),
    ],
    responses={200: PostDetailSerializer}
)
@require_http_methods(["GET"])
def post_detail(request, post_id):
    """获取帖子详情"""
    post = controllers.get_post_detail(post_id)
    
    if not post:
        return JsonResponse({
            'code': 404,
            'message': '帖子不存在'
        }, status=404)
    
    serializer = PostDetailSerializer(post, context={'request': request})
    
    return JsonResponse({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


@extend_schema(
    tags=['社区论坛'],
    summary='创建帖子',
    request=CreatePostSerializer,
    responses={200: PostSerializer}
)
@require_http_methods(["POST"])
@login_required
def create_post(request):
    """创建帖子"""
    serializer = CreatePostSerializer(data=request.data)
    
    if not serializer.is_valid():
        return JsonResponse({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=400)
    
    post = controllers.create_post(
        user=request.user,
        subject=serializer.validated_data['subject'],
        content=serializer.validated_data['content']
    )
    
    result_serializer = PostSerializer(post, context={'request': request})
    
    return JsonResponse({
        'code': 200,
        'message': '发布成功',
        'data': result_serializer.data
    })


@extend_schema(
    tags=['社区论坛'],
    summary='删除帖子',
    parameters=[
        OpenApiParameter(name='post_id', type=int, location=OpenApiParameter.PATH, description='帖子ID'),
    ],
    responses={200: dict}
)
@require_http_methods(["DELETE"])
@login_required
def delete_post(request, post_id):
    """删除帖子"""
    success, message = controllers.delete_post(request.user, post_id)
    
    if not success:
        return JsonResponse({
            'code': 403,
            'message': message
        }, status=403)
    
    return JsonResponse({
        'code': 200,
        'message': message
    })


@extend_schema(
    tags=['社区论坛'],
    summary='切换帖子点赞状态',
    parameters=[
        OpenApiParameter(name='post_id', type=int, location=OpenApiParameter.PATH, description='帖子ID'),
    ],
    responses={200: dict}
)
@require_http_methods(["POST"])
@login_required
def toggle_post_like(request, post_id):
    """切换帖子点赞状态"""
    result, message = controllers.toggle_post_like(request.user, post_id)
    
    if result is None:
        return JsonResponse({
            'code': 404,
            'message': message
        }, status=404)
    
    return JsonResponse({
        'code': 200,
        'message': message,
        'data': {
            'is_liked': result
        }
    })


@extend_schema(
    tags=['社区论坛'],
    summary='创建评论',
    request=CreateCommentSerializer,
    responses={200: CommentSerializer}
)
@require_http_methods(["POST"])
@login_required
def create_comment(request):
    """创建评论"""
    serializer = CreateCommentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return JsonResponse({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=400)
    
    comment, message = controllers.create_comment(
        user=request.user,
        post_id=serializer.validated_data['post'].id,
        content=serializer.validated_data['content']
    )
    
    if not comment:
        return JsonResponse({
            'code': 404,
            'message': message
        }, status=404)
    
    result_serializer = CommentSerializer(comment, context={'request': request})
    
    return JsonResponse({
        'code': 200,
        'message': message,
        'data': result_serializer.data
    })


@extend_schema(
    tags=['社区论坛'],
    summary='获取帖子评论列表',
    parameters=[
        OpenApiParameter(name='post_id', type=int, location=OpenApiParameter.PATH, description='帖子ID'),
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={200: CommentSerializer(many=True)}
)
@require_http_methods(["GET"])
def comment_list(request, post_id):
    """获取帖子评论列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    result, error = controllers.get_post_comments(post_id, page=page, page_size=page_size)
    
    if error:
        return JsonResponse({
            'code': 404,
            'message': error
        }, status=404)
    
    serializer = CommentSerializer(result['comments'], many=True, context={'request': request})
    
    return JsonResponse({
        'code': 200,
        'message': '获取成功',
        'data': {
            'comments': serializer.data,
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages']
            }
        }
    })


@extend_schema(
    tags=['社区论坛'],
    summary='删除评论',
    parameters=[
        OpenApiParameter(name='comment_id', type=int, location=OpenApiParameter.PATH, description='评论ID'),
    ],
    responses={200: dict}
)
@require_http_methods(["DELETE"])
@login_required
def delete_comment(request, comment_id):
    """删除评论"""
    success, message = controllers.delete_comment(request.user, comment_id)
    
    if not success:
        return JsonResponse({
            'code': 403,
            'message': message
        }, status=403)
    
    return JsonResponse({
        'code': 200,
        'message': message
    })


@extend_schema(
    tags=['社区论坛'],
    summary='切换评论点赞状态',
    parameters=[
        OpenApiParameter(name='comment_id', type=int, location=OpenApiParameter.PATH, description='评论ID'),
    ],
    responses={200: dict}
)
@require_http_methods(["POST"])
@login_required
def toggle_comment_like(request, comment_id):
    """切换评论点赞状态"""
    result, message = controllers.toggle_comment_like(request.user, comment_id)
    
    if result is None:
        return JsonResponse({
            'code': 404,
            'message': message
        }, status=404)
    
    return JsonResponse({
        'code': 200,
        'message': message,
        'data': {
            'is_liked': result
        }
    })


@extend_schema(
    tags=['社区论坛'],
    summary='论坛主页 - 获取帖子列表',
    parameters=[
        OpenApiParameter(name='sort_by', type=str, description='排序方式：time(按时间) 或 hot(按热度)，默认time'),
        OpenApiParameter(name='page', type=int, description='页码，默认1'),
        OpenApiParameter(name='page_size', type=int, description='每页数量，默认20'),
    ],
    responses={200: PostHomeSerializer(many=True)}
)
@require_http_methods(["GET"])
def forum_home(request):
    """
    论坛主页 - 获取帖子列表
    
    支持两种排序方式：
    1. time: 按发布时间排序（最新的在前）
    2. hot: 按热度排序（热度 = 点赞数 * 2 + 评论数）
    
    返回帖子的标题和内容前30字预览
    """
    sort_by = request.GET.get('sort_by', 'time')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # 验证排序参数
    if sort_by not in ['time', 'hot']:
        return JsonResponse({
            'code': 400,
            'message': '排序参数错误，仅支持 time 或 hot'
        }, status=400)
    
    result = controllers.get_forum_home(sort_by=sort_by, page=page, page_size=page_size)
    
    serializer = PostHomeSerializer(result['posts'], many=True, context={'request': request})
    
    return JsonResponse({
        'code': 200,
        'message': '获取成功',
        'data': {
            'posts': serializer.data,
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total_pages': result['total_pages']
            },
            'sort_by': result['sort_by']
        }
    })

