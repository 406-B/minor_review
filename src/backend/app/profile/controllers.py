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
    # TODO: 后续实现实际的统计逻辑
    # 目前返回默认值0
    # """获取真实的用户统计"""
    # 获取或创建统计记录
    # stats, created = UserStatistics.objects.get_or_create(user=user)
    
    # return {
    #     'liked_posts_count': stats.liked_posts_count,
    #     'commented_posts_count': stats.commented_posts_count,
    #     'following_count': stats.following_count,
    # }
    return {
        'liked_posts_count': 0,      # 点赞的帖子数量
        'commented_posts_count': 0,  # 评论的帖子数量
        'following_count': 0,        # 关注的人数量
    }
