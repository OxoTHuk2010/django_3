from django.contrib import admin

from apps.catalog.models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель категорий.
    """

    @admin.action(description="Активировать выбранные категории")
    def activate_categories(self, request, queryset) -> None:
        """
        Активировать выбранные категории через массовое действие Django Admin.
        """

        updated_count = queryset.update(is_active=True)

        self.message_user(
            request,
            f"Активировано категорий: {updated_count}",
        )

    @admin.action(description="Деактивировать выбранные категории")
    def deactivate_categories(self, request, queryset) -> None:
        """
        Деактивировать выбранные категории через массовое действие Django Admin.
        """

        updated_count = queryset.update(is_active=False)

        self.message_user(
            request,
            f"Деактивировано категорий: {updated_count}",
        )

    list_display = (
        "id",
        "name",
        "slug",
        "parent",
        "is_active",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "is_deleted",
        "parent",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    ordering = ("name",)
    actions = (
        "activate_categories",
        "deactivate_categories",
    )


class ProductImageInline(admin.TabularInline):
    """
    Inline-форма для изображений товара.

    Позволяет управлять изображениями товара прямо со страницы товара.
    """

    model = ProductImage
    extra = 1
    fields = (
        "image",
        "alt_text",
        "is_main",
        "sort_order",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административная панель товаров.
    """

    @admin.action(description="Активировать выбранные товары")
    def activate_products(self, request, queryset) -> None:
        """
        Активировать выбранные товары через массовое действие Django Admin.
        """

        updated_count = queryset.update(is_active=True)

        self.message_user(
            request,
            f"Активировано товаров: {updated_count}",
        )

    @admin.action(description="Деактивировать выбранные товары")
    def deactivate_products(self, request, queryset) -> None:
        """
        Деактивировать выбранные товары через массовое действие Django Admin.
        """

        updated_count = queryset.update(is_active=False)

        self.message_user(
            request,
            f"Деактивировано товаров: {updated_count}",
        )

    list_display = (
        "id",
        "name",
        "sku",
        "category",
        "price",
        "old_price",
        "stock_quantity",
        "is_active",
        "is_deleted",
        "created_at",
    )
    list_filter = (
        "category",
        "is_active",
        "is_deleted",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
        "sku",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    ordering = ("name",)
    inlines = [
        ProductImageInline,
    ]
    actions = (
        "activate_products",
        "deactivate_products",
    )
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "sku",
                    "description",
                ),
            },
        ),
        (
            "Продажи",
            {
                "fields": (
                    "price",
                    "old_price",
                    "stock_quantity",
                    "is_active",
                ),
            },
        ),
        (
            "Служебная информация",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Отдельная административная панель изображений товаров.
    """

    list_display = (
        "id",
        "product",
        "is_main",
        "sort_order",
        "created_at",
    )
    list_filter = (
        "is_main",
        "created_at",
    )
    search_fields = (
        "product__name",
        "alt_text",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
