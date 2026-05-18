from rest_framework import serializers

from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


class OrderItemSerializer(serializers.ModelSerializer):
    """Позиция заказа с snapshot цены и названия."""

    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "price",
            "quantity",
            "total_price",
        )


class PaymentSummarySerializer(serializers.ModelSerializer):
    """Краткая информация о платеже заказа."""

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "method",
            "amount",
            "currency",
            "provider",
            "paid_at",
        )


class OrderSerializer(serializers.ModelSerializer):
    """Публичное представление заказа текущего пользователя."""

    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "customer_name",
            "customer_email",
            "customer_phone",
            "delivery_address",
            "total_price",
            "comment",
            "items",
            "payments",
            "created_at",
            "updated_at",
        )


class OrderCreateSerializer(serializers.Serializer):
    """Payload API checkout текущей корзины."""

    customer_name = serializers.CharField(max_length=255)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=32)
    shipping_address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)

    def to_shipping_data(self) -> dict[str, str]:
        """Преобразовать API payload в формат `orders.services`."""

        return {
            "customer_name": self.validated_data["customer_name"],
            "customer_email": self.validated_data["customer_email"],
            "customer_phone": self.validated_data["customer_phone"],
            "delivery_address": self.validated_data["shipping_address"],
            "comment": self.validated_data.get("comment", ""),
        }
