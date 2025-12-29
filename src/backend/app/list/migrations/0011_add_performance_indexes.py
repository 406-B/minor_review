# Generated migration for performance optimization
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0010_review_audit_fields'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='floor',
            index=models.Index(fields=['canteen', 'order'], name='list_floor_canteen_order_idx'),
        ),
        migrations.AddIndex(
            model_name='window',
            index=models.Index(fields=['floor', 'order'], name='list_window_floor_order_idx'),
        ),
        migrations.AddIndex(
            model_name='dish',
            index=models.Index(fields=['window'], name='list_dish_window_idx'),
        ),
        migrations.AddIndex(
            model_name='dish',
            index=models.Index(fields=['canteen', '-rating'], name='list_dish_canteen_rating_idx'),
        ),
    ]
