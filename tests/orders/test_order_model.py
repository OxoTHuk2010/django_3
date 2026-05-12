from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def test_order_can_be_created(order, user):
    """Заказ создаётся с пользователем, статусом по умолчанию и нулевой суммой."""
    assert order.user == user
    assert order.status == Order.Status.NEW
    assert order.total_price == Decimal("0.00")
    assert str(order) == f"Заказ #{order.id}"


def test_order_total_price_must_not_be_negative(order):
    """Итоговая сумма заказа не может быть отрицательной."""
    order.total_price = Decimal("-1.00")

    with pytest.raises(IntegrityError, match="orders_order_total_price_gte_0"):
        with transaction.atomic():
            order.save(update_fields=["total_price"])


def test_order_item_total_price(order_item):
    """Стоимость позиции заказа считается по snapshot-цене, сохранённой в OrderItem."""
    assert order_item.total_price == order_item.price * order_item.quantity
    assert str(order_item) == f"{order_item.product_name} x {order_item.quantity}"


def test_order_item_keeps_product_snapshot(order_item, product):
    """Изменение товара после заказа не меняет snapshot названия и цены в OrderItem."""
    product.name = "Changed name"
    product.price = Decimal("999999.00")
    product.save(update_fields=["name", "price"])

    order_item.refresh_from_db()

    assert order_item.product_name == "ThinkPad X1 Carbon"
    assert order_item.price == Decimal("150000.00")


def test_order_recalculate_total_price(order, product, category):
    """Метод пересчёта суммы заказа суммирует все связанные позиции."""
    second_product = baker.make(
        "catalog.Product",
        category=category,
        name="Dock station",
        slug="dock-station",
        sku="SKU-DOCK",
        price=Decimal("20000.00"),
        stock_quantity=3,
    )
    baker.make("orders.OrderItem", order=order, product=product, product_name=product.name, price=Decimal("150000.00"), quantity=2)
    baker.make("orders.OrderItem", order=order, product=second_product, product_name=second_product.name, price=Decimal("20000.00"), quantity=1)

    order.recalculate_total_price()
    order.refresh_from_db()

    assert order.total_price == Decimal("320000.00")


@pytest.mark.parametrize(
    ("field", "value", "constraint"),
    [
        ("price", Decimal("-1.00"), "orders_item_price_gte_0"),
        ("quantity", 0, "orders_item_quantity_gt_0"),
    ],
)
def test_order_item_constraints(order_item, field, value, constraint):
    """Позиция заказа не допускает отрицательную цену и нулевое количество."""
    setattr(order_item, field, value)

    with pytest.raises(IntegrityError, match=constraint):
        with transaction.atomic():
            order_item.save(update_fields=[field])
