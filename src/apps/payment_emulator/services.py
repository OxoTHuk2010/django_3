from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from apps.payments.models import Payment

DEFAULT_PAYMENT_OUTCOME_WEIGHTS: Mapping[str, int] = {
    Payment.Status.SUCCEEDED: 7,
    Payment.Status.FAILED: 1,
    Payment.Status.CANCELLED: 1,
    Payment.Status.PENDING: 1,
}


@dataclass(frozen=True)
class PaymentEmulatorResult:
    """Результат эмуляции ответа платёжного провайдера."""

    status: str
    provider: str = "payment_emulator"
    provider_payment_id: str = ""

    @property
    def is_successful(self) -> bool:
        """Проверить, что эмулятор вернул успешную оплату."""

        return self.status == Payment.Status.SUCCEEDED

    @property
    def should_keep_cart(self) -> bool:
        """Проверить, нужно ли сохранить корзину после ответа провайдера."""

        return not self.is_successful


def emulate_payment_result(
    *,
    weights: Mapping[str, int] | None = None,
    random_source: Callable[[int], int] | None = None,
) -> PaymentEmulatorResult:
    """Вернуть взвешенный результат оплаты с injectable random для тестов."""

    outcome_weights = dict(weights or DEFAULT_PAYMENT_OUTCOME_WEIGHTS)
    _validate_weights(outcome_weights)

    total_weight = sum(outcome_weights.values())
    picker = random_source or random.SystemRandom().randrange
    selected_point = picker(total_weight)

    if selected_point < 0 or selected_point >= total_weight:
        raise ValueError("random_source должен вернуть число в диапазоне от 0 до total_weight - 1.")

    cumulative_weight = 0
    for status, weight in outcome_weights.items():
        cumulative_weight += weight
        if selected_point < cumulative_weight:
            return PaymentEmulatorResult(status=status)

    raise RuntimeError("Не удалось выбрать результат оплаты.")


def _validate_weights(weights: Mapping[str, int]) -> None:
    """Проверить, что веса эмулятора положительные и используют допустимые статусы."""

    allowed_statuses = {
        Payment.Status.SUCCEEDED,
        Payment.Status.FAILED,
        Payment.Status.CANCELLED,
        Payment.Status.PENDING,
    }
    if set(weights) != allowed_statuses:
        raise ValueError("Веса эмулятора должны быть заданы для succeeded, failed, cancelled и pending.")

    if any(weight < 1 for weight in weights.values()):
        raise ValueError("Все веса эмулятора должны быть положительными.")
