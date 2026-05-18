import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from apps.orders.models import Order
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def authenticated_client(user) -> APIClient:
    """Вернуть APIClient с текущим пользователем."""

    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_order_with_product(user, product, status: str = Order.Status.PAID):
    """Создать заказ с товаром для подтверждения права на отзыв."""

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


def test_review_api_lists_only_published_reviews(user, second_user, product):
    """Публичный Review API возвращает только опубликованные отзывы товара."""

    published_review = baker.make(
        "reviews.Review",
        user=user,
        product=product,
        rating=5,
        text="Опубликованный отзыв.",
        status=Review.Status.PUBLISHED,
    )
    baker.make(
        "reviews.Review",
        user=second_user,
        product=product,
        rating=4,
        text="Скрытый отзыв.",
        status=Review.Status.PENDING,
    )

    response = APIClient().get(reverse("api:product-review-list-create", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [published_review.id]


def test_review_api_requires_jwt_for_create(product):
    """Создание отзыва через API требует JWT."""

    response = APIClient().post(
        reverse("api:product-review-list-create", kwargs={"slug": product.slug}),
        {
            "rating": 5,
            "title": "Заголовок",
            "text": "Текст отзыва.",
        },
        format="json",
    )

    assert response.status_code == 401
    assert response.data["code"] == "authentication_required"


def test_review_api_creates_pending_review_for_buyer(user, product):
    """Покупатель может создать отзыв, который уходит на модерацию."""

    make_order_with_product(user, product)

    response = authenticated_client(user).post(
        reverse("api:product-review-list-create", kwargs={"slug": product.slug}),
        {
            "rating": 5,
            "title": "Хороший товар",
            "text": "Покупкой доволен.",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == Review.Status.PENDING
    assert response.data["is_verified_purchase"] is True


def test_review_api_rejects_review_without_purchase(user, product):
    """Пользователь без покупки не может создать отзыв через API."""

    response = authenticated_client(user).post(
        reverse("api:product-review-list-create", kwargs={"slug": product.slug}),
        {
            "rating": 5,
            "title": "",
            "text": "Отзыв без покупки.",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "review_create_error"
