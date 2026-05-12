from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def test_review_can_be_created(review, user, product):
    """Отзыв связывает пользователя и товар, хранит оценку и статус модерации."""
    assert review.user == user
    assert review.product == product
    assert review.rating == 5
    assert review.status == Review.Status.PENDING
    assert user.username in str(review)
    assert product.name in str(review)


def test_review_is_published_property(review):
    """is_published истинно только для опубликованных отзывов."""
    review.status = Review.Status.PUBLISHED

    assert review.is_published is True

    review.status = Review.Status.HIDDEN

    assert review.is_published is False


def test_user_product_pair_is_unique(review, user, product):
    """Один пользователь не может оставить второй отзыв на тот же товар."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make("reviews.Review", user=user, product=product, rating=4, text="Duplicate")


def test_same_user_can_review_different_products(review, user, category):
    """ForeignKey на пользователя позволяет одному пользователю отзываться о разных товарах."""
    second_product = baker.make(
        "catalog.Product",
        category=category,
        name="Monitor",
        slug="monitor",
        sku="SKU-MONITOR",
        price=Decimal("30000.00"),
        stock_quantity=4,
    )

    second_review = baker.make("reviews.Review", user=user, product=second_product, rating=4, text="Good")

    assert second_review.id is not None


def test_different_users_can_review_same_product(review, second_user, product):
    """Разные пользователи могут оставлять отзывы на один и тот же товар."""
    second_review = baker.make("reviews.Review", user=second_user, product=product, rating=4, text="Good")

    assert second_review.id is not None


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_must_be_between_1_and_5(user, product, rating):
    """Оценка отзыва ограничена диапазоном от 1 до 5 на уровне БД."""
    with pytest.raises(IntegrityError, match="reviews_rating_between_1_and_5"):
        with transaction.atomic():
            baker.make("reviews.Review", user=user, product=product, rating=rating, text="Invalid rating")
