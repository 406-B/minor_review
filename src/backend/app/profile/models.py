from django.db import models

# Create your models here.
# 用户模型在login.models.User中
# 这个app主要处理用户资料的业务逻辑，暂时不定义新的模型

# class UserStatistics(models.Model):
#     """用户统计信息 - 独立的统计表"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     total_posts = models.IntegerField(default=0)
#     total_likes = models.IntegerField(default=0)
#     total_followers = models.IntegerField(default=0)
#     last_active = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'profile_statistics'

# class UserPreference(models.Model):
#     """用户偏好设置 - 独立的配置表"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     theme = models.CharField(max_length=20, default='light')  # 主题
#     language = models.CharField(max_length=10, default='zh-cn')  # 语言
#     email_notification = models.BooleanField(default=True)  # 邮件通知
    
#     class Meta:
#         db_table = 'profile_preferences'