import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    """
    Базовый пользователь для тестов
    """

    User = get_user_model()

    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="strong-test-password",
    )
