from decimal import Decimal

import pytest
from django.utils import timezone
from model_bakery import baker

from apps.common.analytics import get_admin_dashboard_analytics, resolve_analytics_period
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def test_resolve_analytics_period_falls_back_to_30_days():
    """Неизвестный период безопасно заменяется периодом за 30 дней."""

    period = resolve_analytics_period("unknown")

    assert period.key == "30d"
    assert period.start_at is not None


def test_admin_dashboard_analytics_counts_core_metrics(user, second_user, product, order):
    """Аналитический слой считает выручку, заказы, пользователей и платежи."""

    order.status = Order.Status.PAID
    order.total_price = Decimal("3000.00")
    order.save(update_fields=["status", "total_price"])
    baker.make(
        "orders.OrderItem",
        order=order,
        product=product,
        product_name=product.name,
        quantity=2,
        price=Decimal("1500.00"),
    )
    baker.make(
        "payments.Payment",
        order=order,
        status=Payment.Status.SUCCEEDED,
        amount=Decimal("3000.00"),
    )
    baker.make(
        "payments.Payment",
        order=order,
        status=Payment.Status.PENDING,
        amount=Decimal("3000.00"),
    )
    baker.make(
        "payments.Payment",
        order=order,
        status=Payment.Status.FAILED,
        amount=Decimal("3000.00"),
    )
    second_user.date_joined = timezone.now()
    second_user.save(update_fields=["date_joined"])

    analytics = get_admin_dashboard_analytics("30d")

    assert analytics["summary"]["revenue"] == Decimal("3000.00")
    assert analytics["summary"]["orders_count"] == 1
    assert analytics["summary"]["average_order_value"] == Decimal("3000.00")
    assert analytics["summary"]["new_users_count"] >= 2
    assert analytics["summary"]["paid_orders_count"] == 1
    assert analytics["summary"]["pending_payments_count"] == 1
    assert analytics["summary"]["failed_payments_count"] == 1


def test_admin_dashboard_analytics_returns_lists_for_operational_work(user, product, review, order):
    """Аналитический слой возвращает списки для остатков, продаж и модерации."""

    product.stock_quantity = 3
    product.save(update_fields=["stock_quantity"])
    order.status = Order.Status.PAID
    order.total_price = Decimal("4500.00")
    order.save(update_fields=["status", "total_price"])
    baker.make(
        "orders.OrderItem",
        order=order,
        product=product,
        product_name=product.name,
        quantity=3,
        price=Decimal("1500.00"),
    )
    review.status = Review.Status.PENDING
    review.save(update_fields=["status"])

    analytics = get_admin_dashboard_analytics("all")

    assert analytics["low_stock_products"][0]["name"] == product.name
    assert analytics["top_products"][0]["product__name"] == product.name
    assert analytics["top_products"][0]["sold_quantity"] == 3
    assert analytics["pending_reviews"][0]["product__name"] == product.name


def test_admin_dashboard_analytics_rounds_average_order_value(user):
    """Средний чек возвращается как денежный Decimal с двумя знаками после запятой."""

    baker.make(
        "orders.Order",
        user=user,
        status=Order.Status.PAID,
        total_price=Decimal("100.00"),
        _quantity=3,
    )

    analytics = get_admin_dashboard_analytics("all")

    assert analytics["summary"]["average_order_value"] == Decimal("100.00")
    assert analytics["summary"]["average_order_value"].as_tuple().exponent == -2
