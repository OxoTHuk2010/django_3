from types import SimpleNamespace

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.exceptions import error_response, validation_error_response
from apps.api.serializers.cart import CartAddSerializer, CartQuantitySerializer, CartSnapshotSerializer
from apps.cart.models import CartItem
from apps.cart.services import add_to_cart, clear_cart, get_cart_snapshot, remove_from_cart, update_cart_item
from apps.catalog.models import Product


class CartRequestMixin:
    """Подготовить request-объект для переиспользования доменного service-layer корзины."""

    def get_service_request(self, request):
        """Вернуть минимальный объект с user/session для cart services."""

        return SimpleNamespace(user=request.user, session={})

    def serialize_snapshot(self, snapshot):
        """Сериализовать snapshot корзины."""

        return CartSnapshotSerializer(snapshot).data


class CartDetailAPIView(CartRequestMixin, APIView):
    """Compatibility endpoint API-корзины текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Вернуть текущее состояние DB-корзины пользователя."""

        snapshot = get_cart_snapshot(self.get_service_request(request))
        return Response(self.serialize_snapshot(snapshot))

    def post(self, request):
        """Добавить товар через совместимый `POST /api/cart/`."""

        return CartItemCreateAPIView().post(request)

    def patch(self, request):
        """Изменить количество позиции через совместимый `PATCH /api/cart/`."""

        serializer = CartAddSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        product_id = serializer.validated_data["product_id"]
        return CartItemDetailAPIView().patch(request, product_id=product_id)

    def delete(self, request):
        """Очистить корзину или удалить позицию через совместимый `DELETE /api/cart/`."""

        product_id = request.data.get("product_id") if hasattr(request, "data") else None
        if product_id:
            try:
                normalized_product_id = int(product_id)
            except (TypeError, ValueError):
                return validation_error_response({"product_id": ["Введите корректный id товара."]})
            return CartItemDetailAPIView().delete(request, product_id=normalized_product_id)

        return CartClearAPIView().delete(request)


class CartItemCreateAPIView(CartRequestMixin, APIView):
    """Добавить товар в API-корзину."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Добавить товар и вернуть обновлённый snapshot корзины."""

        serializer = CartAddSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        product = get_object_or_404(Product.objects.select_related("category"), pk=serializer.validated_data["product_id"])
        result = add_to_cart(
            request=self.get_service_request(request),
            product=product,
            quantity=serializer.validated_data["quantity"],
        )
        if not result.success:
            return error_response(
                code=result.errors[0] if result.errors else "cart_error",
                detail=result.message,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.serialize_snapshot(result.snapshot), status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(CartRequestMixin, APIView):
    """Изменить или удалить позицию API-корзины."""

    permission_classes = (IsAuthenticated,)

    def patch(self, request, product_id: int):
        """Заменить количество позиции корзины."""

        serializer = CartQuantitySerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
        if not CartItem.objects.filter(cart__user=request.user, product=product).exists():
            return error_response(
                code="not_found",
                detail="Позиция корзины не найдена.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        result = update_cart_item(
            request=self.get_service_request(request),
            product=product,
            quantity=serializer.validated_data["quantity"],
        )
        if not result.success:
            return error_response(
                code=result.errors[0] if result.errors else "cart_error",
                detail=result.message,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.serialize_snapshot(result.snapshot))

    def delete(self, request, product_id: int):
        """Удалить позицию из корзины."""

        product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
        result = remove_from_cart(request=self.get_service_request(request), product=product)
        return Response(self.serialize_snapshot(result.snapshot))


class CartClearAPIView(CartRequestMixin, APIView):
    """Очистить API-корзину текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        """Удалить все позиции DB-корзины пользователя."""

        result = clear_cart(self.get_service_request(request))
        return Response(self.serialize_snapshot(result.snapshot))
