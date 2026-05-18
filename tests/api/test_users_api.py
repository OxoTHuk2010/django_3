import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_user_registration_api_creates_user_and_returns_tokens():
    """API-регистрация создаёт пользователя и сразу возвращает JWT pair."""

    response = APIClient().post(
        reverse("api:user-register"),
        {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "StrongApiPassword123",
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

    response = APIClient().post(
        reverse("api:user-register"),
        {
            "username": "newapiuser",
            "email": user.email,
            "password": "StrongApiPassword123",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "email" in response.data["fields"]
