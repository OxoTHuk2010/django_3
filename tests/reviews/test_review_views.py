import pytest
from django.urls import reverse
from model_bakery import baker

from apps.orders.models import Order
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def make_order_with_product(user, product, status: str = Order.Status.PAID):
    """Создать подтверждённый заказ с товаром для web-сценария отзывов."""

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


def review_payload(**kwargs) -> dict[str, str]:
    """Вернуть валидные данные формы отзыва с возможностью точечной замены."""

    payload = {
        "rating": "5",
        "title": "Проверенный отзыв",
        "text": "Товар куплен и проверен в работе.",
    }
    payload.update(kwargs)
    return payload


def test_product_detail_shows_review_form_for_verified_buyer(client, user, product):
    """Покупатель товара видит форму создания отзыва на детальной странице."""

    make_order_with_product(user, product)
    client.force_login(user)

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
    content = response.content.decode()

    assert response.status_code == 200
    assert response.context["review_form"] is not None
    assert reverse("reviews:product_review_add", kwargs={"slug": product.slug}) in content
    assert "Отправить отзыв" in content


def test_product_detail_shows_login_notice_for_guest(client, product):
    """Гость видит объяснение вместо формы отзыва."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["review_form"] is None
    assert "Войдите, чтобы оставить отзыв." in response.content.decode()


def test_product_detail_shows_purchase_notice_for_user_without_order(client, user, product):
    """Пользователь без покупки видит причину недоступности формы отзыва."""

    client.force_login(user)

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["review_form"] is None
    assert "Оставить отзыв могут только покупатели этого товара." in response.content.decode()


def test_product_review_post_creates_pending_review(client, user, product):
    """POST в reviews namespace создаёт отзыв на модерации и возвращает к товару."""

    make_order_with_product(user, product)
    client.force_login(user)

    response = client.post(
        reverse("reviews:product_review_add", kwargs={"slug": product.slug}),
        review_payload(),
    )
    review = Review.objects.get(user=user, product=product)

    assert response.status_code == 302
    assert response.url == f"{reverse('catalog:product_detail', kwargs={'slug': product.slug})}#reviews"
    assert review.status == Review.Status.PENDING
    assert review.is_verified_purchase is True
    assert review.text == "Товар куплен и проверен в работе."


def test_product_review_post_requires_login(client, product):
    """Гость не может создать отзыв через POST-маршрут."""

    response = client.post(
        reverse("reviews:product_review_add", kwargs={"slug": product.slug}),
        review_payload(),
    )

    assert response.status_code == 302
    assert response.url.startswith(reverse("users:login"))
    assert Review.objects.count() == 0


def test_product_review_post_requires_purchase(client, user, product):
    """POST без подтверждённой покупки не создаёт отзыв."""

    client.force_login(user)

    response = client.post(
        reverse("reviews:product_review_add", kwargs={"slug": product.slug}),
        review_payload(),
    )

    assert response.status_code == 302
    assert response.url == f"{reverse('catalog:product_detail', kwargs={'slug': product.slug})}#reviews"
    assert Review.objects.count() == 0


def test_product_review_post_rejects_duplicate_review(client, user, product):
    """POST не создаёт повторный отзыв на тот же товар."""

    make_order_with_product(user, product)
    baker.make(
        "reviews.Review",
        user=user,
        product=product,
        rating=5,
        text="Уже существующий отзыв.",
    )
    client.force_login(user)

    response = client.post(
        reverse("reviews:product_review_add", kwargs={"slug": product.slug}),
        review_payload(),
    )

    assert response.status_code == 302
    assert Review.objects.count() == 1


def test_product_review_post_rejects_invalid_form(client, user, product):
    """Некорректная форма не создаёт отзыв и возвращает пользователя к товару."""

    make_order_with_product(user, product)
    client.force_login(user)

    response = client.post(
        reverse("reviews:product_review_add", kwargs={"slug": product.slug}),
        review_payload(rating="6"),
    )

    assert response.status_code == 302
    assert response.url == f"{reverse('catalog:product_detail', kwargs={'slug': product.slug})}#reviews"
    assert Review.objects.count() == 0
