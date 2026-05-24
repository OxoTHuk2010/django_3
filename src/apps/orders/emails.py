from __future__ import annotations

import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail

from apps.orders.models import Order
from apps.payments.models import Payment

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheckoutEmailResult:
    """Результат best-effort отправки checkout-уведомлений."""

    customer_sent: bool
    admin_sent: bool


def send_checkout_emails(*, order: Order, payment: Payment) -> CheckoutEmailResult:
    """Отправить письма после checkout без риска откатить созданный заказ."""

    customer_sent = _safe_send_customer_email(order=order, payment=payment)
    admin_sent = _safe_send_admin_email(order=order, payment=payment)
    return CheckoutEmailResult(customer_sent=customer_sent, admin_sent=admin_sent)


def _safe_send_customer_email(*, order: Order, payment: Payment) -> bool:
    if not order.customer_email:
        return False

    return _safe_send_mail(
        subject=f"MyShop: заказ #{order.id} создан",
        message=_build_checkout_email_body(order=order, payment=payment, audience="customer"),
        recipient_list=[order.customer_email],
    )


def _safe_send_admin_email(*, order: Order, payment: Payment) -> bool:
    admin_emails = list(getattr(settings, "MYSHOP_ADMIN_EMAILS", []))
    if not admin_emails:
        return False

    return _safe_send_mail(
        subject=f"MyShop: новый заказ #{order.id}",
        message=_build_checkout_email_body(order=order, payment=payment, audience="admin"),
        recipient_list=admin_emails,
    )


def _safe_send_mail(*, subject: str, message: str, recipient_list: list[str]) -> bool:
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception:
        logger.exception("Не удалось отправить checkout email.")
        return False

    return True


def _build_checkout_email_body(*, order: Order, payment: Payment, audience: str) -> str:
    greeting = "Спасибо за заказ в MyShop." if audience == "customer" else "В MyShop создан новый заказ."
    item_lines = [f"- {item.product_name}: {item.quantity} x {item.price} = {item.total_price}" for item in order.items.order_by("id")]

    return "\n".join(
        [
            greeting,
            "",
            f"Номер заказа: #{order.id}",
            f"Статус заказа: {order.get_status_display()}",
            f"Статус оплаты: {payment.get_status_display()}",
            f"Сумма: {order.total_price} {payment.currency}",
            f"Адрес доставки: {order.delivery_address}",
            "",
            "Товары:",
            *(item_lines or ["- Нет позиций заказа"]),
        ],
    )
