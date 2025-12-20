from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "nickname",  "created")
    list_filter = ("created",)
    search_fields = ("username", "nickname")
    readonly_fields = ("created", "updated")
