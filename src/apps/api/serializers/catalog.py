from rest_framework import serializers

from apps.catalog.models import Category, Product, ProductImage
from apps.catalog.selectors import get_product_main_image


class CategorySummarySerializer(serializers.ModelSerializer):
    """Краткая категория для карточек товара."""

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "name",
        )


class ProductImageSerializer(serializers.ModelSerializer):
    """Публичное изображение товара."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = (
            "url",
            "alt_text",
            "is_main",
            "sort_order",
        )

    def get_url(self, obj: ProductImage) -> str:
        """Вернуть URL изображения или пустую строку, если файла нет."""

        if not obj.image:
            return ""
        return obj.image.url


class ProductListSerializer(serializers.ModelSerializer):
    """Компактное представление товара для списка Product API."""

    category = CategorySummarySerializer()
    short_description = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "name",
            "short_description",
            "price",
            "old_price",
            "category",
            "main_image",
            "average_rating",
            "reviews_count",
            "stock_status",
            "url",
        )

    def get_short_description(self, obj: Product) -> str:
        """Вернуть короткое описание для карточки товара."""

        return obj.description[:160]

    def get_main_image(self, obj: Product) -> dict[str, str | bool | int] | None:
        """Вернуть главное изображение товара."""

        image = get_product_main_image(obj)
        if image is None:
            return None
        return ProductImageSerializer(image, context=self.context).data

    def get_average_rating(self, obj: Product) -> str | None:
        """Вернуть средний рейтинг, посчитанный queryset-аннотацией."""

        average_rating = getattr(obj, "average_rating_value", None)
        if average_rating is None:
            return None
        return f"{average_rating:.1f}"

    def get_reviews_count(self, obj: Product) -> int:
        """Вернуть количество опубликованных отзывов."""

        return int(getattr(obj, "reviews_count_value", 0) or 0)

    def get_stock_status(self, obj: Product) -> str:
        """Вернуть публичный статус наличия товара."""

        if obj.stock_quantity < 1:
            return "out_of_stock"
        return "in_stock"

    def get_url(self, obj: Product) -> str:
        """Вернуть API URL детальной карточки товара."""

        return f"/api/products/{obj.slug}/"


class ProductDetailSerializer(ProductListSerializer):
    """Детальное представление товара для Product API."""

    images = ProductImageSerializer(many=True)
    web_url = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "price",
            "old_price",
            "sku",
            "category",
            "images",
            "main_image",
            "average_rating",
            "reviews_count",
            "stock_status",
            "url",
            "web_url",
        )

    def get_web_url(self, obj: Product) -> str:
        """Вернуть web URL карточки товара."""

        return f"/products/{obj.slug}/"
