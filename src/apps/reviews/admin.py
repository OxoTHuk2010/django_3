from django.contrib import admin
from django.utils import timezone

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Административная панель отзывов.
    """

    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "status",
        "is_verified_purchase",
        "created_at",
        "moderated_at",
    )
    list_filter = (
        "status",
        "rating",
        "is_verified_purchase",
        "created_at",
        "moderated_at",
    )
    search_fields = (
        "product__name",
        "product__sku",
        "user__email",
        "title",
        "text",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "moderated_at",
    )
    ordering = ("-created_at",)
    actions = (
        "publish_reviews",
        "reject_reviews",
        "hide_reviews",
    )

    @admin.action(
        description="Опубликовать выбранные отзывы",
    )
    def publish_reviews(
        self,
        request,
        queryset,
    ) -> None:
        """
        Опубликовать выбранные отзывы.

        Используется модератором через Django Admin.
        """

        queryset.update(
            status=Review.Status.PUBLISHED,
            moderated_at=timezone.now(),
        )

    @admin.action(
        description="Отклонить выбранные отзывы",
    )
    def reject_reviews(
        self,
        request,
        queryset,
    ) -> None:
        """
        Отклонить выбранные отзывы.
        """

        queryset.update(
            status=Review.Status.REJECTED,
            moderated_at=timezone.now(),
        )

    @admin.action(
        description="Скрыть выбранные отзывы",
    )
    def hide_reviews(
        self,
        request,
        queryset,
    ) -> None:
        """
        Скрыть выбранные отзывы.
        """

        queryset.update(
            status=Review.Status.HIDDEN,
            moderated_at=timezone.now(),
        )
