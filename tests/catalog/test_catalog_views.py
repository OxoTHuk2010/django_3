from decimal import Decimal

import pytest
from django.urls import reverse
from model_bakery import baker

pytestmark = pytest.mark.django_db


def make_product(category, name: str, slug: str, sku: str, price: str = "1000.00", **kwargs):
    """Создать товар каталога с явными ключевыми полями для проверок web-страниц."""

    defaults = {
        "category": category,
        "name": name,
        "slug": slug,
        "description": f"Описание товара {name}",
        "price": Decimal(price),
        "stock_quantity": 5,
        "sku": sku,
        "is_active": True,
        "is_deleted": False,
    }
    defaults.update(kwargs)
    return baker.make("catalog.Product", **defaults)


def assert_response_contains(response, text: str) -> None:
    """Проверить, что HTML-ответ содержит ожидаемый текст."""

    assert text in response.content.decode()


def assert_response_not_contains(response, text: str) -> None:
    """Проверить, что HTML-ответ не содержит лишний текст."""

    assert text not in response.content.decode()


def test_home_page_shows_public_products(client, product):
    """Главная страница показывает активный неудалённый товар из публичного каталога."""

    response = client.get(reverse("catalog:home"))

    assert response.status_code == 200
    assert_response_contains(response, product.name)


def test_product_list_shows_only_public_products(client, category):
    """Список товаров скрывает неактивные товары, soft-deleted товары и товары из скрытых категорий."""

    visible_product = make_product(category, "Visible Product", "visible-product", "SKU-VISIBLE")
    make_product(category, "Inactive Product", "inactive-product", "SKU-INACTIVE", is_active=False)
    make_product(category, "Deleted Product", "deleted-product", "SKU-DELETED", is_deleted=True)

    hidden_category = baker.make(
        "catalog.Category",
        name="Hidden Category",
        slug="hidden-category",
        is_active=False,
        is_deleted=False,
    )
    make_product(hidden_category, "Hidden Category Product", "hidden-category-product", "SKU-HIDDEN-CATEGORY")

    response = client.get(reverse("catalog:product_list"))

    assert response.status_code == 200
    assert_response_contains(response, visible_product.name)
    assert_response_not_contains(response, "Inactive Product")
    assert_response_not_contains(response, "Deleted Product")
    assert_response_not_contains(response, "Hidden Category Product")


def test_product_list_search_filters_by_name_description_and_sku(client, category):
    """Поиск применяет один пользовательский запрос к названию, описанию и артикулу товара."""

    make_product(category, "ThinkPad Workstation", "thinkpad-workstation", "SKU-THINKPAD")
    make_product(category, "Office Mouse", "office-mouse", "SKU-MOUSE")

    response = client.get(reverse("catalog:product_list"), {"q": "thinkpad"})

    assert response.status_code == 200
    assert_response_contains(response, "ThinkPad Workstation")
    assert_response_not_contains(response, "Office Mouse")


def test_product_list_filters_by_category(client, category):
    """Фильтр категории оставляет товары только из выбранной активной категории."""

    second_category = baker.make(
        "catalog.Category",
        name="Accessories",
        slug="accessories",
    )
    make_product(category, "Notebook Product", "notebook-product", "SKU-NOTEBOOK")
    make_product(second_category, "Accessory Product", "accessory-product", "SKU-ACCESSORY")

    response = client.get(reverse("catalog:product_list"), {"category": "accessories"})

    assert response.status_code == 200
    assert_response_contains(response, "Accessory Product")
    assert_response_not_contains(response, "Notebook Product")


def test_product_list_filters_by_price_range(client, category):
    """Фильтр цены применяет нижнюю и верхнюю границы без падения публичной страницы."""

    make_product(category, "Budget Product", "budget-product", "SKU-BUDGET", price="1200.00")
    make_product(category, "Premium Product", "premium-product", "SKU-PREMIUM", price="9000.00")

    response = client.get(
        reverse("catalog:product_list"),
        {
            "price_min": "1000",
            "price_max": "2000",
        },
    )

    assert response.status_code == 200
    assert_response_contains(response, "Budget Product")
    assert_response_not_contains(response, "Premium Product")


def test_product_list_ignores_invalid_price_filter(client, category):
    """Некорректная цена в GET-параметре игнорируется и не ломает каталог."""

    product = make_product(category, "Safe Product", "safe-product", "SKU-SAFE", price="1200.00")

    response = client.get(reverse("catalog:product_list"), {"price_min": "not-a-number"})

    assert response.status_code == 200
    assert_response_contains(response, product.name)


def test_product_list_sorts_by_price_ascending(client, category):
    """Сортировка `price_asc` показывает более дешёвый товар раньше дорогого."""

    cheap_product = make_product(category, "Cheap Product", "cheap-product", "SKU-CHEAP", price="1000.00")
    expensive_product = make_product(category, "Expensive Product", "expensive-product", "SKU-EXPENSIVE", price="9000.00")

    response = client.get(reverse("catalog:product_list"), {"sort": "price_asc"})
    content = response.content.decode()

    assert response.status_code == 200
    assert content.index(cheap_product.name) < content.index(expensive_product.name)


def test_product_list_paginates_products(client, category):
    """Каталог ограничивает количество товаров на странице и отдаёт данные пагинации."""

    for index in range(7):
        make_product(
            category,
            name=f"Paged Product {index}",
            slug=f"paged-product-{index}",
            sku=f"SKU-PAGED-{index}",
        )

    response = client.get(reverse("catalog:product_list"))

    assert response.status_code == 200
    assert response.context["is_paginated"] is True
    assert len(response.context["products"]) == 6
