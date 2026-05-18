import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from apps.cart.models import CartItem

pytestmark = pytest.mark.django_db


def authenticated_client(user) -> APIClient:
    """Вернуть APIClient с принудительно аутентифицированным пользователем."""

    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_cart_api_requires_jwt():
    """API-корзина недоступна без JWT-аутентификации."""

    response = APIClient().get(reverse("api:cart-detail"))

    assert response.status_code == 401
    assert response.data["code"] == "authentication_required"


def test_cart_api_adds_and_updates_db_cart(user, product):
    """API-корзина работает с DB-cart авторизованного пользователя."""

    client = authenticated_client(user)

    add_response = client.post(
        reverse("api:cart-item-create"),
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert add_response.status_code == 201
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 2
    assert add_response.data["total_quantity"] == 2

    update_response = client.patch(
        reverse("api:cart-item-detail", kwargs={"product_id": product.id}),
        {"quantity": 3},
        format="json",
    )

    assert update_response.status_code == 200
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 3
    assert update_response.data["total_quantity"] == 3


def test_cart_api_rejects_quantity_over_stock(user, product):
    """API-корзина возвращает бизнес-ошибку при превышении остатка."""

    response = authenticated_client(user).post(
        reverse("api:cart-item-create"),
        {
            "product_id": product.id,
            "quantity": product.stock_quantity + 1,
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "quantity_gt_stock"
    assert not CartItem.objects.filter(cart__user=user, product=product).exists()


def test_cart_api_removes_and_clears_items(user, cart, product, category):
    """API-корзина удаляет отдельную позицию и очищает всю корзину."""

    second_product = baker.make(
        "catalog.Product",
        category=category,
        name="Second API Product",
        slug="second-api-product",
        sku="SKU-SECOND-API",
        price=product.price,
        stock_quantity=3,
    )
    baker.make("cart.CartItem", cart=cart, product=product, quantity=1)
    baker.make("cart.CartItem", cart=cart, product=second_product, quantity=1)
    client = authenticated_client(user)

    remove_response = client.delete(reverse("api:cart-item-detail", kwargs={"product_id": product.id}))

    assert remove_response.status_code == 200
    assert not CartItem.objects.filter(cart=cart, product=product).exists()
    assert remove_response.data["total_quantity"] == 1

    clear_response = client.delete(reverse("api:cart-clear"))

    assert clear_response.status_code == 200
    assert cart.items.count() == 0
    assert clear_response.data["is_empty"] is True
