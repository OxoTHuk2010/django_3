import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_user_registration_api_creates_user_and_returns_tokens():
    """API-регистрация создаёт пользователя и сразу возвращает JWT pair."""

    password = f"api-registration-{get_random_string(24)}A1!"
    response = APIClient().post(
        reverse("api:user-register"),
        {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(username="apiuser").exists()
    assert response.data["user"]["username"] == "apiuser"
    assert response.data["tokens"]["access"]
    assert response.data["tokens"]["refresh"]


def test_user_registration_api_requires_unique_email(user):
    """API-регистрация валидирует уникальность email на уровне serializer."""

    password = f"api-registration-{get_random_string(24)}A1!"
    response = APIClient().post(
        reverse("api:user-register"),
        {
            "username": "newapiuser",
            "email": user.email,
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "email" in response.data["fields"]


def test_user_login_api_alias_returns_jwt_pair(user, user_password):
    """Compatibility login endpoint возвращает JWT pair как стандартный token endpoint."""

    response = APIClient().post(
        reverse("api:user-login"),
        {
            "username": user.username,
            "password": user_password,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
