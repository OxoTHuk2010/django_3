from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Административная панель для кастомной модели пользователя.
    """

    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
    )
    ordering = ("email",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": ("phone",),
            },
        ),
    )
