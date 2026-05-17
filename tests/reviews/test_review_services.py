import pytest
from django.contrib.auth.models import AnonymousUser
from model_bakery import baker

from apps.orders.models import Order
from apps.reviews.models import Review
from apps.reviews.services import (
    ReviewCreateError,
    create_product_review,
    get_product_review_availability,
    user_can_review_product,
)

pytestmark = pytest.mark.django_db


def make_order_with_product(user, product, status: str):
    """Создать заказ с товаром для проверки права оставить отзыв."""

    order = baker.make(
        "orders.Order",
        user=user,
        status=status,
        customer_name="Иван Покупатель",
        customer_email="buyer@example.com",
        customer_phone="+70000000000",
        delivery_address="Москва, тестовая улица, 1",
        total_price=product.price,
    )
    baker.make(
        "orders.OrderItem",
        order=order,
        product=product,
        product_name=product.name,
        price=product.price,
        quantity=1,
    )
    return order


@pytest.mark.parametrize(
    "status",
    [
        Order.Status.PAID,
        Order.Status.PROCESSING,
        Order.Status.SHIPPED,
        Order.Status.COMPLETED,
    ],
)
def test_user_can_review_product_for_eligible_order_statuses(user, product, status):
    """Покупка в подтверждённом статусе даёт пользователю право оставить отзыв."""

    make_order_with_product(user, product, status)

    assert user_can_review_product(user, product) is True


@pytest.mark.parametrize(
    "status",
    [
        Order.Status.NEW,
        Order.Status.CANCELLED,
    ],
)
def test_user_cannot_review_product_for_non_eligible_order_statuses(user, product, status):
    """Заказы new и cancelled не подтверждают покупку для отзыва."""

    make_order_with_product(user, product, status)

    assert user_can_review_product(user, product) is False


def test_user_cannot_review_product_without_matching_order_item(user, product, category):
    """Заказ без нужного товара не даёт право оставить отзыв на этот товар."""

    other_product = baker.make(
        "catalog.Product",
        category=category,
        name="Другой товар",
        slug="other-product-for-review",
        sku="SKU-OTHER-REVIEW",
        price=product.price,
        stock_quantity=3,
    )
    make_order_with_product(user, other_product, Order.Status.PAID)

    assert user_can_review_product(user, product) is False


def test_anonymous_user_cannot_review_product(product):
    """Гость не может оставить отзыв даже при прямом вызове service-layer."""

    assert user_can_review_product(AnonymousUser(), product) is False


def test_create_product_review_sets_pending_status_and_verified_purchase(user, product):
    """Разрешённый отзыв создаётся на модерации и помечается как подтверждённая покупка."""

    make_order_with_product(user, product, Order.Status.PAID)

    review = create_product_review(
        user=user,
        product=product,
        rating=5,
        title="Хороший товар",
        text="Покупка прошла успешно, товар понравился.",
    )

    assert review.status == Review.Status.PENDING
    assert review.is_verified_purchase is True
    assert review.rating == 5
    assert review.title == "Хороший товар"


def test_create_product_review_requires_purchase(user, product):
    """Сервис не создаёт отзыв, если пользователь не покупал товар."""

    with pytest.raises(ReviewCreateError, match="покупатели"):
        create_product_review(
            user=user,
            product=product,
            rating=5,
            title="",
            text="Отзыв без покупки.",
        )

    assert Review.objects.count() == 0


def test_create_product_review_rejects_duplicate_review(user, product):
    """Пользователь не может создать второй отзыв на тот же товар."""

    make_order_with_product(user, product, Order.Status.PAID)
    create_product_review(
        user=user,
        product=product,
        rating=5,
        title="Первый отзыв",
        text="Первый текст отзыва.",
    )

    with pytest.raises(ReviewCreateError, match="уже оставили"):
        create_product_review(
            user=user,
            product=product,
            rating=4,
            title="Второй отзыв",
            text="Повторный текст отзыва.",
        )

    assert Review.objects.count() == 1


@pytest.mark.parametrize("rating", [0, 6])
def test_create_product_review_validates_rating(user, product, rating):
    """Сервис проверяет диапазон рейтинга до создания записи."""

    make_order_with_product(user, product, Order.Status.PAID)

    with pytest.raises(ReviewCreateError, match="Оценка"):
        create_product_review(
            user=user,
            product=product,
            rating=rating,
            title="",
            text="Текст отзыва.",
        )

    assert Review.objects.count() == 0


def test_create_product_review_requires_text(user, product):
    """Пустой текст отзыва не проходит бизнес-валидацию."""

    make_order_with_product(user, product, Order.Status.PAID)

    with pytest.raises(ReviewCreateError, match="Текст"):
        create_product_review(
            user=user,
            product=product,
            rating=5,
            title="",
            text="   ",
        )

    assert Review.objects.count() == 0


def test_review_availability_explains_existing_review(user, product):
    """Состояние формы объясняет, почему повторный отзыв недоступен."""

    make_order_with_product(user, product, Order.Status.PAID)
    baker.make(
        "reviews.Review",
        user=user,
        product=product,
        rating=5,
        text="Уже существующий отзыв.",
    )

    availability = get_product_review_availability(user, product)

    assert availability.can_create is False
    assert availability.notice == "Вы уже оставили отзыв на этот товар."
