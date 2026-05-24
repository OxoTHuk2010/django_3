from django.db.models import Avg, Count, Q
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.api.pagination import StandardPageNumberPagination
from apps.api.serializers.catalog import ProductDetailSerializer, ProductListSerializer
from apps.catalog.filters import apply_product_filters
from apps.catalog.selectors import get_product_detail_queryset, get_product_list_queryset
from apps.reviews.models import Review


def with_review_stats(queryset):
    """Добавить статистику опубликованных отзывов к queryset товаров."""

    published_reviews_filter = Q(reviews__status=Review.Status.PUBLISHED)
    return queryset.annotate(
        average_rating_value=Avg("reviews__rating", filter=published_reviews_filter),
        reviews_count_value=Count("reviews", filter=published_reviews_filter),
    )


class ProductListAPIView(ListAPIView):
    """Публичный список товаров REST API."""

    serializer_class = ProductListSerializer
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        """Вернуть публичные товары с фильтрами, сортировкой и статистикой."""

        queryset = with_review_stats(get_product_list_queryset())
        return apply_product_filters(queryset, self.request.query_params)


class ProductDetailAPIView(RetrieveAPIView):
    """Публичная карточка товара REST API."""

    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        """Вернуть только публично доступные товары."""

        return with_review_stats(get_product_detail_queryset())


class ProductDetailByIdAPIView(ProductDetailAPIView):
    """Compatibility-карточка товара по внутреннему id."""

    lookup_field = "pk"
