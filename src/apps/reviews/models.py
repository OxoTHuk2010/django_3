from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel

# Create your models here.


class Review(TimeStampedModel):
    """
    Отзыв пользователя о товаре.

    Модель хранит оценку и текстовый отзыв.

    На текущем этапе отзыв можно связать с пользователем и товаром.
    В будущем можно добавить:
    - проверку факта покупки;
    - жалобы на отзыв;
    - ответы магазина;
    - лайки/дизлайки;
    - историю модерации.
    """

    class Status(models.TextChoices):
        """
        Статусы модерации отзыва.
        """

        DRAFT = "draft", "Черновик"
        PENDING = "pending", "На модерации"
        PUBLISHED = "published", "Опубликован"
        REJECTED = "rejected", "Отклонён"
        HIDDEN = "hidden", "Скрыт"

    user = models.OneToOneField(
        settings.AUTH_USER_MOODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
        help_text="Пользователь, оставивший отзыв.",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар",
        help_text="Товар, к которому относится отзыв.",
    )

    rating = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        help_text="Оценка товара от 1 до 5.",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Заголовок",
        help_text="Краткий заголовок отзыва.",
    )

    text = models.TextField(verbose_name="Текст отзыва", help_text="Основной текст отзыва пользователя.")

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
        help_text="Статус модерации отзыва.",
    )

    is_verified_purchase = models.BooleanField(
        default=False, verbose_name="Подтверждённая покупка", help_text="Признак того, что пользователь действительно покупал товар."
    )

    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата модерации",
        help_text="Дата и время последней модерации отзыва.",
    )

    moderation_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий модератора",
        help_text="Внутренний комментарий модератора по отзыву.",
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "product",
                    "status",
                ],
                name="reviews_product_status_idx",
            ),
            models.Index(
                fields=[
                    "user",
                    "created_at",
                ],
                name="reviews_user_date_idx",
            ),
            models.Index(
                fields=[
                    "rating",
                ],
                name="reviews_rating_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product",
                ],
                name="reviews_unique_user_product",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    rating__gte=1,
                )
                & models.Q(
                    rating__lte=5,
                ),
                name="reviews_rating_between_1_and_5",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое предствавление отзыва.
        """
        return f"Отзыв {self.user} о товаре {self.product}"

    @property
    def is_published(self) -> bool:
        """
        Проверить, опубликован ли отзыв.
        """
        return self.status == self.Status.PUBLISHED
