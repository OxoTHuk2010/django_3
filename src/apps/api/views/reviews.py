from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.exceptions import error_response, validation_error_response
from apps.api.pagination import StandardPageNumberPagination
from apps.api.serializers.reviews import ReviewCreateSerializer, ReviewSerializer
from apps.catalog.selectors import get_product_detail_queryset
from apps.reviews.models import Review
from apps.reviews.services import ReviewCreateError, create_product_review


class ProductReviewListCreateAPIView(APIView):
    """Список опубликованных отзывов и создание нового отзыва товара."""

    permission_classes = (AllowAny,)

    def get(self, request, slug: str):
        """Вернуть опубликованные отзывы публичного товара."""

        product = get_object_or_404(get_product_detail_queryset(), slug=slug)
        queryset = Review.objects.filter(product=product, status=Review.Status.PUBLISHED).select_related("user").order_by("-created_at")
        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, slug: str):
        """Проверить покупку пользователя и создать отзыв на модерации."""

        if not request.user.is_authenticated:
            return error_response(
                code="authentication_required",
                detail="Необходимо выполнить аутентификацию.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        product = get_object_or_404(get_product_detail_queryset(), slug=slug)
        try:
            review = create_product_review(
                user=request.user,
                product=product,
                rating=serializer.validated_data["rating"],
                title=serializer.validated_data.get("title", ""),
                text=serializer.validated_data["text"],
            )
        except ReviewCreateError as error:
            return error_response(
                code="review_create_error",
                detail=str(error),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
