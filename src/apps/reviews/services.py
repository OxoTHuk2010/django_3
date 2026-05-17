from dataclasses import dataclass

from django.db import IntegrityError, transaction

from apps.catalog.models import Product
from apps.orders.models import Order
from apps.reviews.models import Review

REVIEW_ELIGIBLE_ORDER_STATUSES = (
    Order.Status.PAID,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.COMPLETED,
)


class ReviewCreateError(Exception):
    """Ошибка бизнес-правил при создании отзыва."""


@dataclass(frozen=True)
class ReviewAvailability:
    """Результат проверки возможности оставить отзыв на товар."""

    can_create: bool
    notice: str


def user_can_review_product(user, product: Product) -> bool:
    """Проверить, есть ли у пользователя подтверждённая покупка товара."""

    if not user.is_authenticated:
        return False

    return Order.objects.filter(
        user=user,
        status__in=REVIEW_ELIGIBLE_ORDER_STATUSES,
        items__product=product,
    ).exists()


def get_product_review_availability(user, product: Product) -> ReviewAvailability:
    """Вернуть состояние формы отзыва для детальной страницы товара."""

    if not user.is_authenticated:
        return ReviewAvailability(
            can_create=False,
            notice="Войдите, чтобы оставить отзыв.",
        )

    if Review.objects.filter(user=user, product=product).exists():
        return ReviewAvailability(
            can_create=False,
            notice="Вы уже оставили отзыв на этот товар.",
        )

    if not user_can_review_product(user, product):
        return ReviewAvailability(
            can_create=False,
            notice="Оставить отзыв могут только покупатели этого товара.",
        )

    return ReviewAvailability(
        can_create=True,
        notice="",
    )


def create_product_review(
    *,
    user,
    product: Product,
    rating: int,
    title: str = "",
    text: str,
) -> Review:
    """Создать отзыв на товар после проверки покупки и уникальности."""

    if not user.is_authenticated:
        raise ReviewCreateError("Оставить отзыв может только авторизованный пользователь.")

    if not user_can_review_product(user, product):
        raise ReviewCreateError("Оставить отзыв могут только покупатели этого товара.")

    if Review.objects.filter(user=user, product=product).exists():
        raise ReviewCreateError("Вы уже оставили отзыв на этот товар.")

    if rating < 1 or rating > 5:
        raise ReviewCreateError("Оценка должна быть от 1 до 5.")

    normalized_text = text.strip()
    if not normalized_text:
        raise ReviewCreateError("Текст отзыва обязателен.")

    try:
        with transaction.atomic():
            return Review.objects.create(
                user=user,
                product=product,
                rating=rating,
                title=title.strip(),
                text=normalized_text,
                status=Review.Status.PENDING,
                is_verified_purchase=True,
            )
    except IntegrityError as exc:
        raise ReviewCreateError("Не удалось создать отзыв. Проверьте, что отзыв ещё не был отправлен.") from exc
