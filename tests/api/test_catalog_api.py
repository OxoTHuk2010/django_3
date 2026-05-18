from decimal import Decimal

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def make_product(category, name: str, slug: str, sku: str, **kwargs):
    """Создать товар с безопасными публичными значениями для API-тестов."""

    defaults = {
        "category": category,
        "name": name,
        "slug": slug,
        "description": f"Описание {name}",
        "price": Decimal("1000.00"),
        "stock_quantity": 5,
        "sku": sku,
        "is_active": True,
        "is_deleted": False,
    }
    defaults.update(kwargs)
    return baker.make("catalog.Product", **defaults)


def test_product_api_list_shows_only_public_products(category):
    """Product API скрывает неактивные и soft-deleted товары."""

    visible_product = make_product(category, "Visible API Product", "visible-api-product", "SKU-API-VISIBLE")
    make_product(category, "Inactive API Product", "inactive-api-product", "SKU-API-INACTIVE", is_active=False)
    make_product(category, "Deleted API Product", "deleted-api-product", "SKU-API-DELETED", is_deleted=True)

    response = APIClient().get(reverse("api:product-list"))

    assert response.status_code == 200
    names = [item["name"] for item in response.data["results"]]
    assert visible_product.name in names
    assert "Inactive API Product" not in names
    assert "Deleted API Product" not in names


def test_product_api_detail_uses_slug_lookup(product):
    """Детальный Product API открывает товар по slug, а не по id."""

    response = APIClient().get(reverse("api:product-detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.data["slug"] == product.slug
    assert response.data["url"] == f"/api/products/{product.slug}/"


def test_product_api_filters_search_and_category(category):
    """Product API применяет существующие фильтры каталога к публичному queryset."""

    second_category = baker.make("catalog.Category", name="API Accessories", slug="api-accessories")
    make_product(category, "Notebook API", "notebook-api", "SKU-API-NOTEBOOK")
    make_product(second_category, "Mouse API", "mouse-api", "SKU-API-MOUSE")

    response = APIClient().get(
        reverse("api:product-list"),
        {
            "q": "mouse",
            "category": "api-accessories",
        },
    )

    assert response.status_code == 200
    names = [item["name"] for item in response.data["results"]]
    assert names == ["Mouse API"]
