from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from model_bakery import baker

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.reviews.models import Review


@pytest.fixture
def user_password() -> str:
    """Сгенерировать пароль только на время тестового запуска."""

    return f"test-{get_random_string(24)}A1!"


@pytest.fixture
def user(db, user_password):
    """Основной пользователь для проверки связей с доменными моделями."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password=user_password,
    )


@pytest.fixture
def second_user(db, user_password):
    """Дополнительный пользователь для проверки уникальности и прав владения."""
    User = get_user_model()
    return User.objects.create_user(
        username="seconduser",
        email="seconduser@example.com",
        password=user_password,
    )


@pytest.fixture
def category(db):
    """Базовая категория каталога для товаров и вложенности."""
    return baker.make(
        "catalog.Category",
        name="Notebooks",
        slug="notebooks",
    )


@pytest.fixture
def product(db, category):
    """Активный товар с остатком, который можно использовать в корзине и заказах."""
    return baker.make(
        "catalog.Product",
        category=category,
        name="ThinkPad X1 Carbon",
        slug="thinkpad-x1-carbon",
        description="Test product description",
        price=Decimal("150000.00"),
        old_price=Decimal("170000.00"),
        stock_quantity=10,
        sku="SKU-THINKPAD-X1",
        is_active=True,
        is_deleted=False,
    )


@pytest.fixture
def cart(db, user):
    """Постоянная DB-корзина авторизованного пользователя."""
    return baker.make("cart.Cart", user=user)


@pytest.fixture
def cart_item(db, cart, product):
    """Позиция корзины с положительным количеством товара."""
    return baker.make(
        "cart.CartItem",
        cart=cart,
        product=product,
        quantity=2,
    )


@pytest.fixture
def order(db, user):
    """Минимальный заказ без позиций, чтобы отдельно проверять агрегаты."""
    return baker.make(
        "orders.Order",
        user=user,
        status=Order.Status.NEW,
        customer_name="Test Customer",
        customer_email="customer@example.com",
        customer_phone="+70000000000",
        delivery_address="Test address",
        total_price=Decimal("0.00"),
    )


@pytest.fixture
def order_item(db, order, product):
    """Позиция заказа со snapshot названия и цены товара."""
    return baker.make(
        "orders.OrderItem",
        order=order,
        product=product,
        product_name=product.name,
        quantity=2,
        price=product.price,
    )


@pytest.fixture
def payment(db, order):
    """Начальная попытка оплаты заказа через локальный эмулятор оплаты."""
    return baker.make(
        "payments.Payment",
        order=order,
        amount=Decimal("150000.00"),
        status=Payment.Status.PENDING,
        provider="payment_emulator",
    )


@pytest.fixture
def review(db, user, product):
    """Отзыв пользователя о товаре до публикации модератором."""
    return baker.make(
        "reviews.Review",
        user=user,
        product=product,
        rating=5,
        text="Excellent product.",
        status=Review.Status.PENDING,
    )
