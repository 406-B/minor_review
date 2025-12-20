from django.db import models


# Create your models here.
class User(models.Model):
    """
    论坛用户
    """

    username = models.CharField(max_length=32, unique=True, verbose_name="账号")
    password = models.CharField(max_length=255, verbose_name="密码")
    nickname = models.CharField(max_length=255, verbose_name="用户名称")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="头像") # 新增头像字段 11/2 yyf

    # 用户偏好标签（用于个性化推荐）
    preference_tags = models.ManyToManyField(
        'list.Tag',
        blank=True,
        related_name='preferred_by_users',
        verbose_name="偏好标签"
    )

    created = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated = models.DateTimeField(auto_now=True, verbose_name="更新时间")
