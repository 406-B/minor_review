from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings



class Floor(models.Model):
    name = models.CharField(max_length=50, help_text="楼层名称")
    canteen = models.ForeignKey('Canteen', on_delete=models.CASCADE, related_name='floors', help_text="所属食堂")
    order = models.IntegerField(default=0, help_text="排序")
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Floor'
        verbose_name_plural = 'Floors'
    def __str__(self):
        return f"{self.canteen.name} - {self.name}"

class Window(models.Model):
    name = models.CharField(max_length=50, help_text="窗口名称")
    floor = models.ForeignKey('Floor', on_delete=models.CASCADE, related_name='windows', help_text="所属楼层")
    order = models.IntegerField(default=0, help_text="排序")
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Window'
        verbose_name_plural = 'Windows'
    def __str__(self):
        return f"{self.floor.canteen.name}-{self.floor.name}-{self.name}"

class Canteen(models.Model):

    name = models.CharField(max_length=100, unique=True, help_text="Name of the canteen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Canteen'
        verbose_name_plural = 'Canteens'

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    Tag model for labeling dishes with attributes
    Examples: Spicy, Vegetarian, Sweet, Gluten-Free, Popular, etc.
    """

    name = models.CharField(max_length=30, unique=True, help_text="Tag name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Dish(models.Model):

    name = models.CharField(max_length=100, help_text="Name of the dish")
    description = models.TextField(blank=True, help_text="Detailed description of the dish")
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in yuan",
    )
    image = models.ImageField(
        upload_to='dishes/', blank=True, null=True, help_text="Dish photo"
    )
    canteen = models.ForeignKey(
        Canteen,
        on_delete=models.CASCADE,
        related_name='dishes',
        help_text="Which canteen serves this dish",
    )
    window = models.ForeignKey(
        'Window',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dishes',
        help_text="所属窗口（可选）"
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name='dishes', help_text="Tags for filtering and display"
    )
    pending_tags = models.ManyToManyField(
        Tag, blank=True, related_name='pending_dishes',
        help_text="Tags submitted by users, pending admin approval"
    )

    # Rating and popularity
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average rating from 0 to 5",
    )
    view_count = models.IntegerField(
        default=0, help_text="Number of times this dish has been viewed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', 'name']
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['canteen']),
            models.Index(fields=['-rating']),
        ]

    def __str__(self):
        return f"{self.name} - {self.canteen.name}"

    def increment_view_count(self):
        """Increment the view count when a dish is viewed"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

class Rating(models.Model):
    """用户对菜品的评分"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dish_ratings',
        help_text="评分用户"
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="被评分的菜品"
    )
    score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="评分 1-5 分"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['user', 'dish']

    def __str__(self):
        return f"{self.user.username} - {self.dish.name}: {self.score}分"


class Review(models.Model):
    """用户对菜品的文字评论"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dish_reviews',
        help_text="评论用户"
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="被评论的菜品"
    )
    content = models.TextField(help_text="评论内容")
    images = models.JSONField(
        default=list,
        blank=True,
        help_text="评论图片URL列表"
    )
    rating = models.ForeignKey(
        Rating,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        help_text="关联的评分（可选）"
    )
    # 发表时的评分快照（与Rating表独立，后续评分变更不影响已发布评论显示）
    published_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="评论发布时的评分快照"
    )
    likes_count = models.IntegerField(default=0, help_text="点赞数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['dish', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.dish.name}: {self.content[:50]}"
