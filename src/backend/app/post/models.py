from django.db import models
from login.models import User


class Post(models.Model):
    """
    帖子模型
    记录用户发布的帖子信息
    """

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="帖子作者"
    )
    subject = models.CharField(max_length=200, help_text="帖子主题/标题")
    content = models.TextField(help_text="帖子内容")
    images = models.JSONField(
        default=list,
        blank=True,
        help_text="帖子图片URL列表（最多9张）"
    )
    dish = models.ForeignKey(
        'list.Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="关联的菜品（可选）"
    )

    # 审核相关字段
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="审核状态"
    )
    audit_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="审核不通过原因"
    )
    audited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="审核时间"
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    likes_count = models.IntegerField(default=0, help_text="点赞数")
    comments_count = models.IntegerField(default=0, help_text="评论数")

    class Meta:
        ordering = ['-created_at']
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['status', '-created_at']),  # 审核状态+时间
            models.Index(fields=['dish', '-created_at']),  # 菜品相关帖子
            models.Index(fields=['-likes_count']),  # 热门帖子排序
        ]

    def __str__(self):
        return f"{self.author.username} - {self.subject}"


class Comment(models.Model):
    """
    评论模型
    记录用户对帖子的评论
    """

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="所属帖子"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="评论作者"
    )
    content = models.TextField(help_text="评论内容")
    images = models.JSONField(
        default=list,
        blank=True,
        help_text="评论图片URL列表"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="父评论（用于回复功能）"
    )

    # 审核相关字段
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="审核状态"
    )
    audit_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="审核不通过原因"
    )
    audited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="审核时间"
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    likes_count = models.IntegerField(default=0, help_text="点赞数")

    class Meta:
        ordering = ['created_at']
        verbose_name = '评论'
        verbose_name_plural = '评论'
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['post', 'parent', 'created_at']),  # 帖子评论列表
            models.Index(fields=['status', '-created_at']),  # 审核状态
        ]

    def __str__(self):
        return f"{self.author.username} on {self.post.id} - {self.content[:50]}"


class Like(models.Model):
    """
    点赞模型
    记录用户的点赞行为，可以对帖子或评论点赞
    使用 content_type 实现多态关联
    """
    LIKE_TYPE_CHOICES = [
        ('post', '帖子'),
        ('comment', '评论'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="点赞用户"
    )
    like_type = models.CharField(
        max_length=10,
        choices=LIKE_TYPE_CHOICES,
        help_text="点赞类型"
    )
    object_id = models.IntegerField(help_text="被点赞对象的ID")
    created_at = models.DateTimeField(auto_now_add=True, help_text="点赞时间")

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        # 确保一个用户对同一个对象只能点赞一次
        unique_together = [['user', 'like_type', 'object_id']]
        indexes = [
            models.Index(fields=['like_type', 'object_id']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.like_type} {self.object_id}"


class Report(models.Model):
    """
    举报模型
    记录用户对帖子、评论、评价等内容的举报
    """
    REPORT_TYPE_CHOICES = [
        ('post', '帖子'),
        ('comment', '评论'),
        ('review', '评价'),
    ]
    
    REASON_CHOICES = [
        ('political', '政治敏感话题'),
        ('obscene', '淫秽信息'),
        ('advertisement', '恶意广告'),
        ('attack', '人身攻击'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已处理'),
        ('rejected', '已驳回'),
    ]
    
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        help_text="举报人"
    )
    content_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        help_text="被举报内容类型"
    )
    content_id = models.IntegerField(help_text="被举报内容的ID")
    reasons = models.JSONField(
        default=list,
        help_text="举报原因列表"
    )
    description = models.TextField(
        blank=True,
        help_text="补充说明"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="处理状态"
    )
    admin_note = models.TextField(
        blank=True,
        help_text="管理员备注"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="举报时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    
    class Meta:
        verbose_name = '举报'
        verbose_name_plural = '举报'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['reporter']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.content_type} {self.content_id}"
