from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from apps.cart.services import add_to_cart, get_cart_snapshot
from apps.orders.models import Order
from apps.orders.services import CheckoutError, create_order_from_cart
from apps.payments.models import Payment

pytestmark = pytest.mark.django_db


def make_request(user):
    """Создать request с session для проверки checkout service через cart service."""

    request = RequestFactory().get("/checkout/")
    middleware = SessionMiddleware(lambda current_request: None)
    middleware.process_request(request)
    request.session.save()
    request.user = user
    return request


def make_shipping_data() -> dict[str, str]:
    """Вернуть минимальные данные доставки, которые соответствуют форме checkout."""

    return {
        "customer_name": "Иван Покупатель",
        "customer_email": "buyer@example.com",
        "customer_phone": "+70000000000",
        "delivery_address": "Москва, тестовая улица, 1",
        "comment": "Позвонить перед доставкой.",
    }


def test_create_order_from_cart_creates_paid_order_and_payment(user, product):
    """Checkout создаёт заказ, позиции, успешный mock-платёж и уменьшает остаток."""

    request = make_request(user)
    add_to_cart(request, product, 2)
    snapshot = get_cart_snapshot(request)

    order = create_order_from_cart(
        user=user,
        cart_snapshot=snapshot,
        shipping_data=make_shipping_data(),
    )

    product.refresh_from_db()
    payment = Payment.objects.get(order=order)
    order_item = order.items.get()

    assert order.status == Order.Status.PAID
    assert order.total_price == Decimal("300000.00")
    assert order_item.product_name == product.name
    assert order_item.price == Decimal("150000.00")
    assert order_item.quantity == 2
    assert product.stock_quantity == 8
    assert payment.status == Payment.Status.SUCCEEDED
    assert payment.provider == "mock"
    assert payment.amount == order.total_price
    assert payment.paid_at is not None


def test_create_order_from_cart_rechecks_stock_inside_transaction(user, product):
    """Если остаток изменился после просмотра корзины, заказ не создаётся."""

    request = make_request(user)
    add_to_cart(request, product, 2)
    snapshot = get_cart_snapshot(request)
    product.stock_quantity = 1
    product.save(update_fields=["stock_quantity"])

    with pytest.raises(CheckoutError, match="Недостаточно товара"):
        create_order_from_cart(
            user=user,
            cart_snapshot=snapshot,
            shipping_data=make_shipping_data(),
        )

    product.refresh_from_db()
    assert product.stock_quantity == 1
    assert Order.objects.count() == 0
    assert Payment.objects.count() == 0


def test_create_order_from_cart_requires_authenticated_user(product):
    """Сервис не создаёт заказ для гостя, даже если snapshot корзины валиден."""

    request = make_request(AnonymousUser())
    add_to_cart(request, product, 1)
    snapshot = get_cart_snapshot(request)

    with pytest.raises(CheckoutError, match="только авторизованным"):
        create_order_from_cart(
            user=AnonymousUser(),
            cart_snapshot=snapshot,
            shipping_data=make_shipping_data(),
        )

    assert Order.objects.count() == 0
