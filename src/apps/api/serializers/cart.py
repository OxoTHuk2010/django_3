from rest_framework import serializers


class CartProductSerializer(serializers.Serializer):
    """Товар внутри snapshot API-корзины."""

    id = serializers.IntegerField()
    slug = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    url = serializers.CharField()
    web_url = serializers.CharField()


class CartItemSnapshotSerializer(serializers.Serializer):
    """Позиция snapshot корзины."""

    product = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_available = serializers.BooleanField()
    availability_message = serializers.CharField(allow_null=True)

    def get_product(self, obj) -> dict:  # noqa: ANN001
        """Вернуть краткие данные товара позиции."""

        product = obj.product
        return {
            "id": product.id,
            "slug": product.slug,
            "name": product.name,
            "price": product.price,
            "url": f"/api/products/{product.slug}/",
            "web_url": f"/products/{product.slug}/",
        }


class CartSnapshotSerializer(serializers.Serializer):
    """Нормализованное состояние корзины."""

    items = CartItemSnapshotSerializer(many=True)
    total_quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    available_total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_empty = serializers.BooleanField()
    has_unavailable_items = serializers.BooleanField()
    can_checkout = serializers.BooleanField()
    warnings = serializers.ListField(child=serializers.CharField())


class CartAddSerializer(serializers.Serializer):
    """Payload добавления товара в API-корзину."""

    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CartQuantitySerializer(serializers.Serializer):
    """Payload изменения количества позиции API-корзины."""

    quantity = serializers.IntegerField(min_value=1)
