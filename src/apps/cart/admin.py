from django.contrib import admin

from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline-форма для позиций корзины.
    """

    model = CartItem
    extra = 0
    fields = (
        "product",
        "quantity",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Административная панель корзин.
    """

    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [
        CartItemInline,
    ]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Административная панель позиций корзины.
    """

    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "cart__user__email",
        "product__name",
        "product__sku",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
