from django.db import models
from django.utils import timezone

# Create your models here.


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с датами создания и обновления.

    Используется как базовый класс для сущностей, где важно понимать:
    - когда запись была создана;
    - когда запись была изменена в последний раз.

    Такую модель удобно наследовать почти во всех бизнес-сущностях:
    товарах, категориях, заказах, позициях заказа и так далее.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Дата и время создания записи.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
        help_text="Дата и время последнего обновления записи.",
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель для мягкого удаления.

    Мягкое удаление означает, что запись физически остаётся в базе данных,
    но помечается как удалённая.

    Это полезно, когда нельзя терять историю:
    - товары могли быть в заказах;
    - категории могли использоваться в аналитике;
    - данные могут понадобиться для аудита.
    """

    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Удалено",
        help_text="Признак мягкого удаления записи.",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата удаления",
        help_text="Дата и время мягкого удаления записи.",
    )

    def soft_delete(self) -> None:
        """
        Пометить запись как удалённую.

        Метод не удаляет объект из базы физически,
        а только выставляет флаг is_deleted=True.
        """

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ],
        )

    def restore(self) -> None:
        """
        Восстановить мягко удалённую запись.

        Метод снимает флаг удаления и очищает дату удаления.
        """

        self.is_deleted = False
        self.deleted_at = None
        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ],
        )

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Абстрактная модель с признаком активности.

    Используется для объектов, которые можно временно выключить
    без удаления из базы данных.

    Например:
    - товар временно скрыт с витрины;
    - категория временно не отображается;
    - промокод отключён.
    """

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Определяет, доступна ли запись для использования.",
    )

    class Meta:
        abstract = True
