from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['dish', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.dish.name} - {self.rating}"
