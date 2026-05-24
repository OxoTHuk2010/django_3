import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils.crypto import get_random_string

pytestmark = pytest.mark.django_db


def test_user_can_be_created_with_username_and_email():
    """Пользователь создаётся со стандартным username-логином и контактным email."""
    User = get_user_model()
    password = f"test-user-{get_random_string(24)}A1!"

    user = User.objects.create_user(
        username="john",
        email="john@example.com",
        password=password,
    )

    assert user.id is not None
    assert user.username == "john"
    assert user.email == "john@example.com"
    assert user.check_password(password)


def test_user_uses_username_as_login_field():
    """ADR 0007 зафиксировал username как основное поле аутентификации."""
    User = get_user_model()

    assert User.USERNAME_FIELD == "username"
    assert User.REQUIRED_FIELDS == []


def test_user_email_is_optional():
    """Email является вспомогательным контактным полем и может быть пустым."""
    User = get_user_model()

    user = User.objects.create_user(username="without-email", password=f"test-user-{get_random_string(24)}A1!")

    # Django может сохранить пустой email как NULL или пустую строку в зависимости от пути создания.
    assert user.email in (None, "")


def test_user_email_is_unique_when_provided(user):
    """Если email указан, база должна отклонять повторное значение."""
    User = get_user_model()

    with pytest.raises(IntegrityError):
        # atomic изолирует ожидаемую ошибку уникальности и не ломает транзакцию теста.
        with transaction.atomic():
            User.objects.create_user(
                username="duplicate-email",
                email=user.email,
                password=f"test-user-{get_random_string(24)}A1!",
            )


def test_user_string_representation(user):
    """Строковое представление пользователя возвращает username для admin и связанных моделей."""
    assert str(user) == user.username
