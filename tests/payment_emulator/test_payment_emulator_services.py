import pytest

from apps.payment_emulator.services import DEFAULT_PAYMENT_OUTCOME_WEIGHTS, emulate_payment_result
from apps.payments.models import Payment


def test_payment_emulator_uses_default_weights():
    """Дефолтные веса соответствуют ADR 0033."""

    assert DEFAULT_PAYMENT_OUTCOME_WEIGHTS == {
        Payment.Status.SUCCEEDED: 7,
        Payment.Status.FAILED: 1,
        Payment.Status.CANCELLED: 1,
        Payment.Status.PENDING: 1,
    }


@pytest.mark.parametrize(
    ("selected_point", "expected_status"),
    [
        (0, Payment.Status.SUCCEEDED),
        (6, Payment.Status.SUCCEEDED),
        (7, Payment.Status.FAILED),
        (8, Payment.Status.CANCELLED),
        (9, Payment.Status.PENDING),
    ],
)
def test_payment_emulator_allows_deterministic_outcomes(selected_point, expected_status):
    """Подменяемый источник случайности позволяет стабильно проверить все исходы."""

    result = emulate_payment_result(random_source=lambda total_weight: selected_point)

    assert result.status == expected_status


def test_payment_emulator_rejects_invalid_random_source():
    """Эмулятор явно отклоняет random source вне допустимого диапазона."""

    with pytest.raises(ValueError, match="random_source"):
        emulate_payment_result(random_source=lambda total_weight: total_weight)
