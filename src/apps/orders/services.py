from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cart.services import CartSnapshot
from apps.catalog.models import Product
from apps.orders.emails import send_checkout_emails
from apps.orders.models import Order, OrderItem
from apps.payment_emulator.services import PaymentEmulatorResult, emulate_payment_result
from apps.payments.models import Payment


class CheckoutError(Exception):
    """Ошибка бизнес-правил checkout, которую можно безопасно показать пользователю."""


@dataclass(frozen=True)
class CheckoutLine:
    """Позиция заказа после повторной проверки товара внутри транзакции."""

    product: Product
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass(frozen=True)
class CheckoutResult:
    """Результат checkout с решением, можно ли очищать корзину."""

    order: Order
    payment: Payment
    payment_result: PaymentEmulatorResult

    @property
    def should_clear_cart(self) -> bool:
        """Корзина очищается только после успешной оплаты."""

        return self.payment_result.is_successful


def create_order_from_cart(
    *,
    user,
    cart_snapshot: CartSnapshot,
    shipping_data: dict[str, Any],
    payment_random_source: Callable[[int], int] | None = None,
) -> CheckoutResult:
    """Создать заказ из snapshot корзины и применить результат payment emulator."""

    if not getattr(user, "is_authenticated", False):
        raise CheckoutError("Оформление заказа доступно только авторизованным пользователям.")

    if not cart_snapshot.can_checkout:
        raise CheckoutError("Корзина пуста или содержит товары, недоступные для оформления.")

    snapshot_items = sorted(cart_snapshot.items, key=lambda item: item.product.id)
    if not snapshot_items:
        raise CheckoutError("Нельзя оформить пустую корзину.")

    with transaction.atomic():
        locked_products = _get_locked_products(snapshot_items)
        checkout_lines = _build_checkout_lines(snapshot_items, locked_products)
        total_price = sum((line.total_price for line in checkout_lines), Decimal("0.00"))

        payment_result = emulate_payment_result(random_source=payment_random_source)
        order_status = Order.Status.PAID if payment_result.is_successful else Order.Status.NEW

        order = Order.objects.create(
            user=user,
            status=order_status,
            customer_name=shipping_data["customer_name"],
            customer_email=shipping_data["customer_email"],
            customer_phone=shipping_data["customer_phone"],
            delivery_address=shipping_data["delivery_address"],
            comment=shipping_data.get("comment", ""),
            total_price=total_price,
        )

        for line in checkout_lines:
            OrderItem.objects.create(
                order=order,
                product=line.product,
                product_name=line.product.name,
                price=line.unit_price,
                quantity=line.quantity,
            )

        if payment_result.is_successful:
            for line in checkout_lines:
                line.product.stock_quantity -= line.quantity
                line.product.save(update_fields=["stock_quantity", "updated_at"])

        payment = Payment.objects.create(
            order=order,
            status=payment_result.status,
            method=Payment.Method.OTHER,
            amount=total_price,
            provider=payment_result.provider,
            provider_payment_id=payment_result.provider_payment_id,
            paid_at=timezone.now() if payment_result.is_successful else None,
        )

    checkout_result = CheckoutResult(
        order=order,
        payment=payment,
        payment_result=payment_result,
    )
    send_checkout_emails(order=checkout_result.order, payment=checkout_result.payment)
    return checkout_result


def _get_locked_products(snapshot_items) -> dict[int, Product]:
    product_ids = [item.product.id for item in snapshot_items]
    products = Product.objects.select_for_update().select_related("category").filter(id__in=product_ids).order_by("id")
    return {product.id: product for product in products}


def _build_checkout_lines(snapshot_items, locked_products: dict[int, Product]) -> list[CheckoutLine]:
    checkout_lines: list[CheckoutLine] = []

    for item in snapshot_items:
        product = locked_products.get(item.product.id)
        if product is None or not _is_product_visible(product):
            raise CheckoutError(f"Товар «{item.product.name}» больше недоступен для оформления.")

        if item.quantity > product.stock_quantity:
            raise CheckoutError(f"Недостаточно товара «{product.name}» на складе.")

        checkout_lines.append(
            CheckoutLine(
                product=product,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=product.price * item.quantity,
            ),
        )

    return checkout_lines


def _is_product_visible(product: Product) -> bool:
    return product.is_active and not product.is_deleted and product.category.is_active and not product.category.is_deleted
