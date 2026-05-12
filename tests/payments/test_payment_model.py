from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

from apps.payments.models import Payment

pytestmark = pytest.mark.django_db


def test_payment_can_be_created(payment, order):
    """Платёж создаётся как запись попытки оплаты конкретного заказа."""
    assert payment.order == order
    assert payment.amount == Decimal("150000.00")
    assert payment.status == Payment.Status.PENDING
    assert payment.provider == "mock"
    assert str(payment) == f"Платёж #{payment.id} по заказу #{order.id}"


def test_payment_amount_must_not_be_negative(payment):
    """Сумма платежа не может быть отрицательной."""
    payment.amount = Decimal("-1.00")

    with pytest.raises(IntegrityError, match="payments_amount_gte_0"):
        with transaction.atomic():
            payment.save(update_fields=["amount"])


def test_payment_success_property(payment):
    """is_successful истинно только для статуса succeeded."""
    payment.status = Payment.Status.SUCCEEDED

    assert payment.is_successful is True

    payment.status = Payment.Status.FAILED

    assert payment.is_successful is False


@pytest.mark.parametrize(
    "status",
    [
        Payment.Status.SUCCEEDED,
        Payment.Status.FAILED,
        Payment.Status.CANCELLED,
        Payment.Status.REFUNDED,
    ],
)
def test_payment_final_statuses(payment, status):
    """Финальные статусы платежа больше не требуют ожидания внешней операции."""
    payment.status = status

    assert payment.is_final is True


def test_payment_pending_is_not_final(payment):
    """Статус pending не считается финальным, потому что платёж ещё ожидает результата."""
    payment.status = Payment.Status.PENDING

    assert payment.is_final is False


def test_order_can_have_multiple_payments(order):
    """ADR 0008 разрешает нескольким Payment ссылаться на один Order."""
    first_payment = baker.make("payments.Payment", order=order, amount=Decimal("100.00"), status=Payment.Status.FAILED)
    second_payment = baker.make("payments.Payment", order=order, amount=Decimal("100.00"), status=Payment.Status.PENDING)

    assert list(order.payments.order_by("id")) == [first_payment, second_payment]
