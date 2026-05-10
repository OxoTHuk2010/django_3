from django.db import models

from apps.common.models import ActiveModel, SoftDeleteModel, TimeStampedModel


class Category(
    TimeStampedModel,
    ActiveModel,
    SoftDeleteModel,
):
    """
    Категория товаров.

    Категории поддерживают вложенность через поле parent.

    Примеры:
    - Электроника
      - Ноутбуки
      - Смартфоны
    - Одежда
      - Мужская одежда
      - Женская одежда
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Название категории, отображаемое пользователю.",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="Уникальный человекочитаемый идентификатор для URL.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Описание категории. Может использоваться на странице категории.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
        help_text="Родительская категория для построения дерева категорий.",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = [
            "name",
        ]
        indexes = [
            models.Index(
                fields=[
                    "slug",
                ],
                name="catalog_category_slug_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "is_deleted",
                ],
                name="catalog_category_state_idx",
            ),
            models.Index(
                fields=[
                    "parent",
                    "is_active",
                ],
                name="catalog_category_parent_idx",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление категории.
        """

        return self.name


class Product(
    TimeStampedModel,
    ActiveModel,
    SoftDeleteModel,
):
    """
    Товар интернет-магазина.

    Важные решения:
    - цена хранится в DecimalField, не во FloatField;
    - остаток хранится в stock_quantity;
    - sku уникален;
    - slug уникален;
    - категория защищена от случайного удаления через PROTECT.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
        help_text="Категория, к которой относится товар.",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Название товара, отображаемое пользователю.",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="Уникальный человекочитаемый идентификатор товара для URL.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Подробное описание товара.",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Текущая цена товара.",
    )
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена",
        help_text="Старая цена товара. Может использоваться для отображения скидки.",
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Остаток на складе",
        help_text="Количество доступных единиц товара.",
    )
    sku = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Артикул",
        help_text="Уникальный артикул товара.",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = [
            "name",
        ]
        indexes = [
            models.Index(
                fields=[
                    "slug",
                ],
                name="catalog_product_slug_idx",
            ),
            models.Index(
                fields=[
                    "sku",
                ],
                name="catalog_product_sku_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "is_deleted",
                ],
                name="catalog_product_state_idx",
            ),
            models.Index(
                fields=[
                    "category",
                    "is_active",
                ],
                name="catalog_product_category_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    price__gte=0,
                ),
                name="catalog_product_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    old_price__gte=0,
                )
                | models.Q(
                    old_price__isnull=True,
                ),
                name="catalog_product_old_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    stock_quantity__gte=0,
                ),
                name="catalog_product_stock_gte_0",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление товара.
        """

        return self.name

    @property
    def is_available(self) -> bool:
        """
        Проверить, доступен ли товар для покупки.

        Товар считается доступным, если:
        - он активен;
        - он не удалён;
        - остаток на складе больше нуля.
        """

        return self.is_active and not self.is_deleted and self.stock_quantity > 0


class ProductImage(TimeStampedModel):
    """
    Изображение товара.

    Один товар может иметь несколько изображений.
    Поле is_main позволяет отметить главное изображение товара.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
        help_text="Товар, к которому относится изображение.",
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        verbose_name="Изображение",
        help_text="Файл изображения товара.",
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Alt-текст",
        help_text="Текстовое описание изображения для SEO и доступности.",
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Главное изображение",
        help_text="Определяет, является ли изображение главным для товара.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Порядок отображения изображения среди других изображений товара.",
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = [
            "sort_order",
            "id",
        ]
        indexes = [
            models.Index(
                fields=[
                    "product",
                    "is_main",
                ],
                name="catalog_product_image_main_idx",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление изображения товара.
        """

        return f"Изображение товара: {self.product.name}"
