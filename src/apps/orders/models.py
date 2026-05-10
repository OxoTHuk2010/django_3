from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Order(TimeStampedModel):
    """
    Заказ пользователя.

    Заказ фиксирует состояние покупки на момент оформления.

    Поэтому в заказе хранятся:
    - контактное имя;
    - email;
    - телефон;
    - адрес доставки;
    - итоговая сумма.

    Эти данные не стоит каждый раз брать из пользователя,
    потому что пользователь может изменить профиль после оформления заказа.
    История заказа при этом должна остаться корректной.
    """

    class Status(models.TextChoices):
        """
        Возможные статусы заказа.
        """

        NEW = "new", "Новый"
        PAID = "paid", "Оплачен"
        PROCESSING = "processing", "В обработке"
        SHIPPED = "shipped", "Отправлен"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Пользователь",
        help_text="Пользователь, оформивший заказ.",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус",
        help_text="Текущий статус заказа.",
    )

    customer_name = models.CharField(
        max_length=255,
        verbose_name="Имя покупателя",
        help_text="Имя покупателя на момент оформления заказа.",
    )
    customer_email = models.EmailField(
        verbose_name="Email покупателя",
        help_text="Email покупателя на момент оформления заказа.",
    )
    customer_phone = models.CharField(
        max_length=32,
        verbose_name="Телефон покупателя",
        help_text="Телефон покупателя на момент оформления заказа.",
    )
    delivery_address = models.TextField(
        verbose_name="Адрес доставки",
        help_text="Адрес доставки, указанный при оформлении заказа.",
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Итоговая сумма",
        help_text="Итоговая сумма заказа.",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
        help_text="Комментарий покупателя к заказу.",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = [
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "status",
                ],
                name="orders_order_user_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="orders_order_status_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    total_price__gte=0,
                ),
                name="orders_order_total_price_gte_0",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление заказа.
        """

        return f"Заказ #{self.id}"

    def recalculate_total_price(self) -> None:
        """
        Пересчитать итоговую стоимость заказа по позициям.

        Метод суммирует total_price всех связанных OrderItem
        и сохраняет результат в поле total_price.
        """

        total = sum(item.total_price for item in self.items.all())

        self.total_price = total
        self.save(
            update_fields=[
                "total_price",
            ],
        )


class OrderItem(TimeStampedModel):
    """
    Позиция заказа.

    Важное архитектурное решение:
    цена и название товара копируются в OrderItem на момент заказа.

    Это нужно, потому что Product может измениться:
    - товар могут переименовать;
    - цену могут изменить;
    - товар могут скрыть или удалить;
    - остатки могут измениться.

    Исторический заказ при этом должен оставаться неизменным.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
        help_text="Заказ, к которому относится позиция.",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар",
        help_text="Связанный товар из каталога.",
    )
    product_name = models.CharField(
        max_length=255,
        verbose_name="Название товара",
        help_text="Название товара на момент оформления заказа.",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Цена товара на момент оформления заказа.",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        help_text="Количество единиц товара в заказе.",
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        ordering = [
            "id",
        ]
        indexes = [
            models.Index(
                fields=[
                    "order",
                    "product",
                ],
                name="orders_item_order_product_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    price__gte=0,
                ),
                name="orders_item_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity__gt=0,
                ),
                name="orders_item_quantity_gt_0",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление позиции заказа.
        """

        return f"{self.product_name} x {self.quantity}"

    @property
    def total_price(self):
        """
        Итоговая стоимость позиции заказа.

        Считается по зафиксированной цене OrderItem.price,
        а не по текущей цене Product.price.
        """

        return self.price * self.quantity
