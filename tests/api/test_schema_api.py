import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_openapi_schema_is_available():
    """OpenAPI schema доступна после подключения доменных API endpoints."""

    response = APIClient().get(reverse("schema"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "/api/products/" in content
    assert "/api/cart/" in content
    assert "/api/orders/" in content
