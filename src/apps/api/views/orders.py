from types import SimpleNamespace

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.exceptions import error_response, validation_error_response
from apps.api.pagination import StandardPageNumberPagination
from apps.api.serializers.orders import OrderCreateSerializer, OrderSerializer
from apps.cart.services import clear_cart, get_cart_snapshot
from apps.orders.models import Order
from apps.orders.services import CheckoutError, create_order_from_cart


class OrderQuerysetMixin:
    """Общий queryset заказов только для текущего пользователя."""

    def get_queryset(self):
        """Скрыть чужие заказы через фильтр queryset и 404."""

        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "payments").order_by("-created_at")


class OrderListCreateAPIView(OrderQuerysetMixin, ListAPIView):
    """Список заказов и API checkout текущего пользователя."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPageNumberPagination

    def post(self, request):
        """Создать заказ из текущей корзины и очистить корзину после успеха."""

        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        service_request = SimpleNamespace(user=request.user, session={})
        cart_snapshot = get_cart_snapshot(service_request)
        try:
            order = create_order_from_cart(
                user=request.user,
                cart_snapshot=cart_snapshot,
                shipping_data=serializer.to_shipping_data(),
            )
        except CheckoutError as error:
            return error_response(
                code=_checkout_error_code(cart_snapshot),
                detail=str(error),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        clear_cart(service_request)
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(OrderQuerysetMixin, RetrieveAPIView):
    """Детальная карточка заказа текущего пользователя."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)


def _checkout_error_code(cart_snapshot) -> str:  # noqa: ANN001
    if cart_snapshot.is_empty:
        return "cart_empty"
    if cart_snapshot.has_unavailable_items:
        return "cart_has_unavailable_items"
    return "checkout_error"
