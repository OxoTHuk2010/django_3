import pytest
from django.urls import reverse

from apps.cart.models import CartItem
from apps.orders.models import Order
from apps.payment_emulator.services import PaymentEmulatorResult
from apps.payments.models import Payment

pytestmark = pytest.mark.django_db


def checkout_payload() -> dict[str, str]:
    """Данные формы checkout для web-тестов."""

    return {
        "customer_name": "Иван Покупатель",
        "customer_email": "buyer@example.com",
        "customer_phone": "+70000000000",
        "delivery_address": "Москва, тестовая улица, 1",
        "comment": "",
    }


def test_checkout_requires_login(client, product):
    """Гость с валидной корзиной перенаправляется на страницу входа."""

    session = client.session
    session["cart"] = {str(product.id): 1}
    session.save()

    response = client.get(reverse("orders:checkout"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("users:login"))


def test_checkout_page_opens_for_authenticated_user_with_valid_cart(client, user, cart, product):
    """Авторизованный пользователь с валидной корзиной видит форму оформления."""

    client.force_login(user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    response = client.get(reverse("orders:checkout"))

    assert response.status_code == 200
    assert "Оформление заказа" in response.content.decode()


def test_checkout_post_creates_order_and_clears_cart(client, user, cart, product, monkeypatch):
    """POST checkout при успешной оплате создаёт заказ и очищает DB-корзину."""

    client.force_login(user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    monkeypatch.setattr(
        "apps.orders.services.emulate_payment_result",
        lambda **kwargs: PaymentEmulatorResult(status=Payment.Status.SUCCEEDED),
    )

    response = client.post(reverse("orders:checkout"), checkout_payload())

    order = Order.objects.get(user=user)
    product.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse("users:order_detail", kwargs={"pk": order.pk})
    assert order.items.count() == 1
    assert Payment.objects.filter(order=order, status=Payment.Status.SUCCEEDED).exists()
    assert product.stock_quantity == 8
    assert cart.items.count() == 0


def test_checkout_post_keeps_cart_when_payment_failed(client, user, cart, product, monkeypatch):
    """POST checkout при неуспешной оплате сохраняет корзину и не списывает остаток."""

    client.force_login(user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    monkeypatch.setattr(
        "apps.orders.services.emulate_payment_result",
        lambda **kwargs: PaymentEmulatorResult(status=Payment.Status.FAILED),
    )

    response = client.post(reverse("orders:checkout"), checkout_payload())

    order = Order.objects.get(user=user)
    product.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse("users:order_detail", kwargs={"pk": order.pk})
    assert order.status == Order.Status.NEW
    assert Payment.objects.filter(order=order, status=Payment.Status.FAILED).exists()
    assert product.stock_quantity == 10
    assert cart.items.count() == 1


def test_checkout_redirects_to_cart_when_cart_is_empty(client, user):
    """Пустая корзина не допускается к checkout."""

    client.force_login(user)

    response = client.get(reverse("orders:checkout"))

    assert response.status_code == 302
    assert response.url == reverse("cart:detail")
