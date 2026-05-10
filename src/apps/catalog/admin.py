from django.contrib import admin

from apps.catalog.models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель категорий.
    """

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
