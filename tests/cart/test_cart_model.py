from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_cart_belongs_to_user(cart, user):
    """DB-корзина принадлежит авторизованному пользователю."""
    assert cart.user == user
    assert str(cart).endswith(user.username)


def test_user_can_have_only_one_cart(cart, user):
    """Для авторизованного пользователя допускается только одна постоянная DB-корзина."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make("cart.Cart", user=user)


def test_cart_item_total_price(cart_item, product):
    """Стоимость позиции корзины считается из актуальной цены товара и количества."""
    assert cart_item.total_price == product.price * cart_item.quantity
    assert str(cart_item) == f"{product.name} x {cart_item.quantity}"


def test_cart_total_items_and_total_price(cart, product, category):
    """Итоги корзины вычисляются динамически по всем позициям."""
    second_product = baker.make(
        "catalog.Product",
        category=category,
        name="Mouse",
        slug="mouse",
        sku="SKU-MOUSE",
        price=Decimal("2500.00"),
        stock_quantity=5,
    )
    baker.make("cart.CartItem", cart=cart, product=product, quantity=2)
    baker.make("cart.CartItem", cart=cart, product=second_product, quantity=3)

    assert cart.total_items == 5
    assert cart.total_price == Decimal("307500.00")


def test_cart_item_product_is_unique_per_cart(cart, product):
    """Один товар не может быть добавлен в одну корзину двумя строками."""
    baker.make("cart.CartItem", cart=cart, product=product, quantity=1)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make("cart.CartItem", cart=cart, product=product, quantity=2)


def test_cart_item_quantity_must_be_positive(cart, product):
    """Количество позиции корзины должно быть строго положительным."""
    with pytest.raises(IntegrityError, match="cart_item_quantity_gt_0"):
        with transaction.atomic():
            baker.make("cart.CartItem", cart=cart, product=product, quantity=0)
