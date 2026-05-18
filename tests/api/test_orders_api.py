import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from apps.cart.models import CartItem
from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def authenticated_client(user) -> APIClient:
    """Вернуть APIClient с текущим пользователем."""

    client = APIClient()
    client.force_authenticate(user=user)
    return client


def checkout_payload() -> dict[str, str]:
    """Вернуть валидные контактные данные API checkout."""

    return {
        "customer_name": "Иван Покупатель",
        "customer_email": "buyer@example.com",
        "customer_phone": "+79990000000",
        "shipping_address": "Москва, ул. Тестовая, 1",
        "comment": "Позвонить перед доставкой.",
    }


def test_order_api_requires_jwt():
    """API заказов недоступен без JWT."""

    response = APIClient().get(reverse("api:order-list"))

    assert response.status_code == 401
    assert response.data["code"] == "authentication_required"


def test_order_api_creates_order_from_current_cart(user, cart, product):
    """POST /api/orders/ создаёт заказ из текущей DB-корзины и очищает её."""

    baker.make("cart.CartItem", cart=cart, product=product, quantity=2)
    initial_stock = product.stock_quantity

    response = authenticated_client(user).post(reverse("api:order-list"), checkout_payload(), format="json")

    assert response.status_code == 201
    assert response.data["status"] == Order.Status.PAID
    assert response.data["items"][0]["product_name"] == product.name
    assert response.data["payments"][0]["provider"] == "mock"
    assert not CartItem.objects.filter(cart=cart).exists()

    product.refresh_from_db()
    assert product.stock_quantity == initial_stock - 2


def test_order_api_returns_only_current_user_orders(user, second_user, order):
    """Пользователь видит только собственные заказы."""

    other_order = baker.make(
        "orders.Order",
        user=second_user,
        customer_name="Другой покупатель",
        customer_email="other@example.com",
        customer_phone="+70000000001",
        delivery_address="Другой адрес",
    )

    client = authenticated_client(user)
    list_response = client.get(reverse("api:order-list"))
    detail_response = client.get(reverse("api:order-detail", kwargs={"pk": other_order.pk}))

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.data["results"]] == [order.id]
    assert detail_response.status_code == 404
    assert detail_response.data["code"] == "not_found"


def test_order_api_rejects_empty_cart(user):
    """Нельзя создать заказ из пустой API-корзины."""

    response = authenticated_client(user).post(reverse("api:order-list"), checkout_payload(), format="json")

    assert response.status_code == 400
    assert response.data["code"] == "cart_empty"
