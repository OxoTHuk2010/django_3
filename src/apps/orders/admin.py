from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline-форма для позиций заказа.
    """

    model = OrderItem
    extra = 0
    fields = (
        "product",
        "product_name",
        "price",
        "quantity",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Административная панель заказов.
    """

    @admin.action(description="Отменить выбранные заказы")
    def cancel_orders(self, request, queryset) -> None:
        """
        Перевести выбранные заказы в статус отмены через Django Admin.
        """

        updated_count = queryset.update(status=Order.Status.CANCELLED)

        self.message_user(
            request,
            f"Отменено заказов: {updated_count}",
        )

    list_display = (
        "id",
        "user",
        "status",
        "customer_name",
        "customer_email",
        "customer_phone",
        "total_price",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "customer_name",
        "customer_email",
        "customer_phone",
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [
        OrderItemInline,
    ]
    actions = ("cancel_orders",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Административная панель позиций заказа.
    """

    list_display = (
        "id",
        "order",
        "product",
        "product_name",
        "price",
        "quantity",
        "created_at",
    )
    search_fields = (
        "order__customer_email",
        "product__name",
        "product__sku",
        "product_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
