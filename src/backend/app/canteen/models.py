from django.db import models
from login.models import User


class CanteenConsumption(models.Model):
    """
    用户食堂消费记录
    存储从清华一卡通系统爬取的食堂消费数据
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='canteen_consumption',
        verbose_name='用户'
    )
    idserial = models.CharField(
        max_length=32,
        verbose_name='学号',
        help_text='清华大学学号'
    )
    servicehall_cookie = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='ServiceHall Cookie',
        help_text='用于访问一卡通系统的认证cookie'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='总消费金额',
        help_text='单位：元'
    )
    canteen_count = models.IntegerField(
        default=0,
        verbose_name='食堂数量',
        help_text='消费过的食堂数量'
    )
    canteen_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='食堂消费详情',
        help_text='各食堂消费金额，格式: {"食堂名": 金额}'
    )
    last_fetched = models.DateTimeField(
        auto_now=True,
        verbose_name='最后更新时间'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'canteen_consumption'
        verbose_name = '食堂消费记录'
        verbose_name_plural = '食堂消费记录'
        ordering = ['-last_fetched']

    def __str__(self):
        return f'{self.user.username} - {self.idserial} - ¥{self.total_amount}'
