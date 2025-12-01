from django.db import transaction
from .models import Post, Comment, Like


def create_post(user, subject, content, dish=None):
    """
    创建帖子
    参数:
        user: 用户对象
        subject: 帖子标题
        content: 帖子内容
        dish: 关联的菜品对象（可选）
    """
    post = Post.objects.create(
        author=user,
        subject=subject,
        content=content,
        dish=dish
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
        post = Post.objects.select_related('author', 'dish__canteen').prefetch_related(
            'comments__author',
            'comments__replies__author'  # 预加载回复评论
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


def create_comment(user, post_id, content, images=None, parent_id=None):
    """
    创建评论
    参数:
        user: 用户对象
        post_id: 帖子ID
        content: 评论内容
        images: 图片列表（可选）
        parent_id: 父评论ID（可选，用于回复）
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None, "帖子不存在"
    
    # 验证父评论
    parent_comment = None
    if parent_id:
        try:
            parent_comment = Comment.objects.get(id=parent_id, post=post)
            # 防止多级回复（只允许回复顶级评论）
            if parent_comment.parent is not None:
                return None, "只能回复顶级评论"
        except Comment.DoesNotExist:
            return None, "父评论不存在"

    with transaction.atomic():
        comment = Comment.objects.create(
            post=post,
            author=user,
            content=content,
            images=images or [],
            parent=parent_comment
        )
        # 更新帖子评论数
        post.comments_count += 1
        post.save(update_fields=['comments_count'])
        
        if parent_comment:
            return comment, "回复成功"
        else:
            return comment, "评论成功"


def get_post_comments(post_id, page=1, page_size=20):
    """
    获取帖子的评论列表（仅顶级评论，回复在序列化器中处理）
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None, "帖子不存在"

    offset = (page - 1) * page_size
    # 只获取顶级评论（parent为null）
    comments = Comment.objects.filter(
        post=post, 
        parent__isnull=True
    ).select_related('author').prefetch_related(
        'replies__author'  # 预加载回复及其作者
    )[offset:offset + page_size]
    
    total = Comment.objects.filter(post=post, parent__isnull=True).count()
    
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
    删除顶级评论时会同时删除所有回复
    """
    try:
        comment = Comment.objects.get(id=comment_id, author=user)
        post = comment.post
        
        with transaction.atomic():
            # 如果是顶级评论，计算要删除的总数（包括回复）
            if comment.parent is None:
                reply_count = comment.replies.count()
                total_deleted = 1 + reply_count
            else:
                total_deleted = 1
            
            comment.delete()  # 级联删除会自动删除回复
            
            # 更新帖子评论数
            post.comments_count = max(0, post.comments_count - total_deleted)
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
    # 基础查询，预加载菜品信息
    posts = Post.objects.select_related('author', 'dish__canteen').all()
    
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


def get_dish_posts(dish_id, page=1, page_size=20):
    """
    获取关联某个菜品的帖子列表
    
    参数:
        dish_id: 菜品ID
        page: 页码
        page_size: 每页数量
    
    返回:
        包含帖子列表和分页信息的字典
    """
    # 查询关联特定菜品的帖子
    posts = Post.objects.filter(dish_id=dish_id).select_related(
        'author', 'dish__canteen'
    ).order_by('-created_at')
    
    # 分页
    offset = (page - 1) * page_size
    posts_page = posts[offset:offset + page_size]
    total = posts.count()
    
    return {
        'posts': posts_page,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
