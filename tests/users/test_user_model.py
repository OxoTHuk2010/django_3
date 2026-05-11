import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_user_can_be_created_with_username_and_email():
    """
    Проверяем базовое создание пользователя.

    По текущему решению:
    - username является основным логином;
    - email является вспомогательным полем.
    """

    User = get_user_model()

    user = User.objects.create_user(
        username="John",
        email="john@example.com",
        password="secure-password",
    )

    assert user.id is not None
    assert user.username == "John"
    assert user.email == "john@example.com"
    assert user.check_password("secure-password")
