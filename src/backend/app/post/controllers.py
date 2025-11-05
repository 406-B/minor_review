from django.db import transaction
from .models import Post, Comment, Like


def create_post(user, subject, content):
    """
    创建帖子
    """
    post = Post.objects.create(
        author=user,
        subject=subject,
        content=content
    )
    return post


def get_post_list(page=1, page_size=20):
    """
    获取帖子列表（分页）
    """
    offset = (page - 1) * page_size
    posts = Post.objects.select_related('author').all()[offset:offset + page_size]
    total = Post.objects.count()
    return {
        'posts': posts,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


def get_post_detail(post_id):
    """
    获取帖子详情（包含评论）
    """
    try:
        post = Post.objects.select_related('author').prefetch_related(
            'comments__author'
        ).get(id=post_id)
        return post
    except Post.DoesNotExist:
        return None


def toggle_post_like(user, post_id):
    """
    切换帖子点赞状态
    如果已点赞则取消，未点赞则添加
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None, "帖子不存在"

    with transaction.atomic():
        like, created = Like.objects.get_or_create(
            user=user,
            like_type='post',
            object_id=post_id
        )
        
        if created:
            # 新增点赞
            post.likes_count += 1
            post.save(update_fields=['likes_count'])
            return True, "点赞成功"
        else:
            # 取消点赞
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save(update_fields=['likes_count'])
            return False, "取消点赞"


def create_comment(user, post_id, content):
    """
    创建评论
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None, "帖子不存在"

    with transaction.atomic():
        comment = Comment.objects.create(
            post=post,
            author=user,
            content=content
        )
        # 更新帖子评论数
        post.comments_count += 1
        post.save(update_fields=['comments_count'])
        return comment, "评论成功"


def get_post_comments(post_id, page=1, page_size=20):
    """
    获取帖子的评论列表
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None, "帖子不存在"

    offset = (page - 1) * page_size
    comments = Comment.objects.filter(post=post).select_related('author')[offset:offset + page_size]
    total = Comment.objects.filter(post=post).count()
    
    return {
        'comments': comments,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }, None


def toggle_comment_like(user, comment_id):
    """
    切换评论点赞状态
    """
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return None, "评论不存在"

    with transaction.atomic():
        like, created = Like.objects.get_or_create(
            user=user,
            like_type='comment',
            object_id=comment_id
        )
        
        if created:
            # 新增点赞
            comment.likes_count += 1
            comment.save(update_fields=['likes_count'])
            return True, "点赞成功"
        else:
            # 取消点赞
            like.delete()
            comment.likes_count = max(0, comment.likes_count - 1)
            comment.save(update_fields=['likes_count'])
            return False, "取消点赞"


def get_user_posts(user_id, page=1, page_size=20):
    """
    获取用户发布的帖子列表
    """
    offset = (page - 1) * page_size
    posts = Post.objects.filter(author_id=user_id).select_related('author')[offset:offset + page_size]
    total = Post.objects.filter(author_id=user_id).count()
    
    return {
        'posts': posts,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


def delete_post(user, post_id):
    """
    删除帖子（只能删除自己的帖子）
    """
    try:
        post = Post.objects.get(id=post_id, author=user)
        post.delete()
        return True, "删除成功"
    except Post.DoesNotExist:
        return False, "帖子不存在或无权限删除"


def delete_comment(user, comment_id):
    """
    删除评论（只能删除自己的评论）
    """
    try:
        comment = Comment.objects.get(id=comment_id, author=user)
        post = comment.post
        comment.delete()
        # 更新帖子评论数
        post.comments_count = max(0, post.comments_count - 1)
        post.save(update_fields=['comments_count'])
        return True, "删除成功"
    except Comment.DoesNotExist:
        return False, "评论不存在或无权限删除"


def get_user_recent_posts(user_id, limit=3):
    """
    获取用户最近发布的帖子
    """
    posts = Post.objects.filter(author_id=user_id).order_by('-created_at')[:limit]
    return posts


def get_user_liked_posts(user_id, page=1, page_size=20):
    """
    获取用户点赞过的帖子列表
    """
    # 获取用户点赞的帖子ID列表
    liked_post_ids = Like.objects.filter(
        user_id=user_id,
        like_type='post'
    ).values_list('object_id', flat=True)
    
    # 分页查询帖子
    offset = (page - 1) * page_size
    posts = Post.objects.filter(id__in=liked_post_ids).order_by('-created_at')[offset:offset + page_size]
    total = len(liked_post_ids)
    
    return {
        'posts': posts,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 0
    }


def get_user_comments(user_id, page=1, page_size=20):
    """
    获取用户发出的所有评论
    """
    offset = (page - 1) * page_size
    comments = Comment.objects.filter(author_id=user_id).select_related('post', 'author').order_by('-created_at')[offset:offset + page_size]
    total = Comment.objects.filter(author_id=user_id).count()
    
    return {
        'comments': comments,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }


def get_forum_home(sort_by='time', page=1, page_size=20):
    """
    获取论坛主页帖子列表
    支持按时间或热度排序
    
    参数:
        sort_by: 排序方式，'time'(按发布时间) 或 'hot'(按热度)
        page: 页码
        page_size: 每页数量
    
    返回:
        包含帖子列表和分页信息的字典
    """
    # 基础查询
    posts = Post.objects.select_related('author').all()
    
    # 根据排序方式选择不同的排序字段
    if sort_by == 'hot':
        # 热度排序：综合点赞数和评论数
        # 使用公式：热度 = likes_count * 2 + comments_count
        # 点赞权重更高，因为点赞表示更强的认同
        posts = posts.extra(
            select={'hotness': 'likes_count * 2 + comments_count'}
        ).order_by('-hotness', '-created_at')
    else:
        # 时间排序：按创建时间倒序
        posts = posts.order_by('-created_at')
    
    # 分页
    offset = (page - 1) * page_size
    posts_page = posts[offset:offset + page_size]
    total = posts.count()
    
    return {
        'posts': posts_page,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
        'sort_by': sort_by
    }
