import pytest
from django.urls import reverse

from apps.cart.models import CartItem

pytestmark = pytest.mark.django_db


def assert_response_contains(response, text: str) -> None:
    """Проверить наличие ожидаемого текста в HTML-ответе."""

    assert text in response.content.decode()


def test_cart_detail_opens_empty_cart(client):
    """Страница корзины открывается и показывает пустое состояние."""

    response = client.get(reverse("cart:detail"))

    assert response.status_code == 200
    assert_response_contains(response, "Корзина пока пуста")


def test_cart_add_view_adds_product_to_guest_session(client, product):
    """POST-добавление товара сохраняет позицию в session-cart гостя."""

    response = client.post(
        reverse("cart:add", kwargs={"product_id": product.id}),
        {"quantity": "2"},
    )

    assert response.status_code == 302
    assert response.url == reverse("cart:detail")
    assert client.session["cart"] == {str(product.id): 2}


def test_cart_update_view_changes_guest_quantity(client, product):
    """POST-изменение количества заменяет значение в session-cart."""

    session = client.session
    session["cart"] = {str(product.id): 2}
    session.save()

    response = client.post(
        reverse("cart:update", kwargs={"product_id": product.id}),
        {"quantity": "4"},
    )

    assert response.status_code == 302
    assert client.session["cart"][str(product.id)] == 4


def test_cart_remove_view_deletes_guest_item(client, product):
    """POST-удаление товара очищает позицию гостевой корзины."""

    session = client.session
    session["cart"] = {str(product.id): 2}
    session.save()

    response = client.post(reverse("cart:remove", kwargs={"product_id": product.id}))

    assert response.status_code == 302
    assert "cart" not in client.session


def test_cart_clear_view_deletes_guest_cart(client, product):
    """POST-очистка удаляет все позиции гостевой корзины."""

    session = client.session
    session["cart"] = {str(product.id): 2}
    session.save()

    response = client.post(reverse("cart:clear"))

    assert response.status_code == 302
    assert "cart" not in client.session


def test_cart_mutation_does_not_allow_get(client, product):
    """GET-запрос к mutating endpoint не должен менять корзину."""

    response = client.get(reverse("cart:add", kwargs={"product_id": product.id}))

    assert response.status_code == 405
    assert "cart" not in client.session


def test_product_detail_has_active_cart_form(client, product):
    """На этапе 8 карточка товара содержит активную POST-форму добавления в корзину."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert_response_contains(response, f'action="{reverse("cart:add", kwargs={"product_id": product.id})}"')
    assert_response_contains(response, 'method="post"')
    assert_response_contains(response, "Добавить в корзину")


def test_product_detail_keeps_disabled_state_for_out_of_stock_product(client, product):
    """Товар без остатка не получает активную форму добавления в корзину."""

    product.stock_quantity = 0
    product.save(update_fields=["stock_quantity"])

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert_response_contains(response, "Нет в наличии")
    assert f'action="{reverse("cart:add", kwargs={"product_id": product.id})}"' not in response.content.decode()


def test_authenticated_cart_add_view_uses_db_cart(client, user, product):
    """Авторизованный пользователь через web-view пишет позицию в DB-корзину."""

    client.force_login(user)

    response = client.post(
        reverse("cart:add", kwargs={"product_id": product.id}),
        {"quantity": "2"},
    )

    assert response.status_code == 302
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 2
    assert "cart" not in client.session


def test_cart_detail_has_checkout_link_for_valid_cart(client, product):
    """Валидная корзина показывает ссылку на оформление заказа."""

    session = client.session
    session["cart"] = {str(product.id): 1}
    session.save()

    response = client.get(reverse("cart:detail"))

    assert response.status_code == 200
    assert_response_contains(response, reverse("orders:checkout"))
    assert_response_contains(response, "Оформить заказ")
