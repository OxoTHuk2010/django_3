from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Cart(TimeStampedModel):
    """
    Корзина пользователя.

    На текущем этапе корзина привязана только к авторизованному пользователю.

    Гостевую корзину через session_key будет добавлена позже,
    когда появится полноценный API и сценарии работы с сессиями.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
        help_text="Пользователь, которому принадлежит корзина.",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        ordering = [
            "-created_at",
        ]

    def __str__(self) -> str:
        """
        Строковое представление корзины.
        """

        return f"Корзина пользователя {self.user}"

    @property
    def total_price(self):
        """
        Итоговая стоимость всех товаров в корзине.

        Значение считается динамически по позициям корзины.
        В базовой версии не сохраняется в отдельное поле.
        """

        return sum(
            item.total_price
            for item in self.items.select_related(
                "product",
            )
        )

    @property
    def total_items(self) -> int:
        """
        Общее количество товаров в корзине.

        Считается как сумма quantity по всем позициям корзины.
        """

        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    """
    Позиция корзины.

    Одна позиция соответствует одному товару в конкретной корзине.
    Ограничение unique_product_in_cart не даёт добавить один и тот же
    товар в одну корзину несколькими строками.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
        help_text="Корзина, к которой относится позиция.",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name="Товар",
        help_text="Товар, добавленный в корзину.",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
        help_text="Количество единиц товара в корзине.",
    )

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        ordering = [
            "id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "product",
                ],
                name="cart_unique_product_in_cart",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity__gt=0,
                ),
                name="cart_item_quantity_gt_0",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "cart",
                    "product",
                ],
                name="cart_item_cart_product_idx",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление позиции корзины.
        """

        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """
        Итоговая стоимость позиции корзины.

        Рассчитывается как текущая цена товара, умноженная на количество.
        """

        return self.product.price * self.quantity
