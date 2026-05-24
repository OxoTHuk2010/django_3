import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string

from apps.cart.models import CartItem

pytestmark = pytest.mark.django_db


def test_profile_requires_login(client):
    """Личный кабинет закрыт для гостя."""

    response = client.get(reverse("users:profile"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("users:login"))


def test_profile_opens_for_authenticated_user(client, user):
    """Авторизованный пользователь открывает свой профиль."""

    client.force_login(user)

    response = client.get(reverse("users:profile"))

    assert response.status_code == 200
    assert user.username in response.content.decode()


def test_login_merges_guest_cart_to_user_db_cart(client, user, user_password, product):
    """После входа гостевая корзина объединяется с DB-корзиной пользователя."""

    session = client.session
    session["cart"] = {str(product.id): 2}
    session.save()

    response = client.post(
        reverse("users:login"),
        {
            "username": user.username,
            "password": user_password,
        },
    )

    assert response.status_code == 302
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 2
    assert "cart" not in client.session


def test_registration_creates_user_and_logs_in(client):
    """Регистрация создаёт пользователя и сразу открывает личный кабинет."""

    password = f"test-registration-{get_random_string(24)}A1!"
    response = client.post(
        reverse("users:register"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": password,
            "password2": password,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("users:profile")
    assert "_auth_user_id" in client.session


def test_user_sees_only_own_orders(client, user, second_user, order):
    """Детальная страница заказа фильтруется по текущему пользователю."""

    order.user = second_user
    order.save(update_fields=["user"])
    client.force_login(user)

    response = client.get(reverse("users:order_detail", kwargs={"pk": order.pk}))

    assert response.status_code == 404


def test_profile_edit_updates_current_user(client, user):
    """Пользователь может редактировать только собственные профильные поля."""

    client.force_login(user)

    response = client.post(
        reverse("users:profile_edit"),
        {
            "email": "updated@example.com",
            "first_name": "Иван",
            "last_name": "Покупатель",
            "phone": "+70000000001",
        },
    )

    user.refresh_from_db()
    assert response.status_code == 302
    assert user.email == "updated@example.com"
    assert user.first_name == "Иван"
    assert user.phone == "+70000000001"
