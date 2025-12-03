"""
用户个人资料业务逻辑控制器
"""


def update_user_profile(user, nickname=None, avatar=None):
    """
    更新用户资料

    Args:
        user: User对象
        nickname: 新昵称（可选）
        avatar: 新头像文件（可选）

    Returns:
        (success: bool, message: str)
    """
    try:
        if nickname is not None:
            user.nickname = nickname
        if avatar is not None:
            user.avatar = avatar
        user.save()
        return True, "更新成功"
    except Exception as e:
        print(e)
        return False, str(e)


def update_user_password(user, new_password):
    """
    更新用户密码

    Args:
        user: User对象
        new_password: 加密后的新密码

    Returns:
        (success: bool, message: str)
    """
    try:
        user.password = new_password
        user.save()
        return True, "密码修改成功"
    except Exception as e:
        print(e)
        return False, str(e)


def get_user_stats(user):
    """
    获取用户统计信息

    Args:
        user: User对象

    Returns:
        dict: 包含统计信息的字典
    """
    from post.models import Post, Comment, Like

    # 统计用户点赞的帖子数量
    liked_posts_count = Like.objects.filter(
        user=user,
        like_type='post'
    ).count()

    # 统计用户评论的数量（总数，不去重）
    comments_count = Comment.objects.filter(
        author=user
    ).count()

    # 统计用户发布的帖子数量
    posts_count = Post.objects.filter(author=user).count()

    # TODO: 添加关注数统计
    following_count = 0

    return {
        'liked_posts_count': liked_posts_count,      # 点赞的帖子数量
        'comments_count': comments_count,  # 评论数量（总数）
        'posts_count': posts_count,  # 发布的帖子数量
        'following_count': following_count,        # 关注的人数量（未实现）
    }
