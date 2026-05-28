from decimal import Decimal

import pytest
from django.urls import reverse
from model_bakery import baker

from apps.reviews.models import Review

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
    """Каталог по умолчанию показывает 12 товаров на странице и отдаёт данные пагинации."""

    for index in range(13):
        make_product(
            category,
            name=f"Paged Product {index}",
            slug=f"paged-product-{index}",
            sku=f"SKU-PAGED-{index}",
        )

    response = client.get(reverse("catalog:product_list"))

    assert response.status_code == 200
    assert response.context["is_paginated"] is True
    assert len(response.context["products"]) == 12


def test_product_list_allows_safe_page_size_options(client, category):
    """Каталог разрешает пользователю выбрать только поддерживаемый размер страницы."""

    for index in range(25):
        make_product(
            category,
            name=f"Large Page Product {index}",
            slug=f"large-page-product-{index}",
            sku=f"SKU-LARGE-PAGE-{index}",
        )

    response = client.get(reverse("catalog:product_list"), {"per_page": "24"})

    assert response.status_code == 200
    assert response.context["is_paginated"] is True
    assert len(response.context["products"]) == 24
    assert response.context["filter_state"]["per_page"] == "24"


def test_product_list_ignores_unsupported_page_size(client, category):
    """Неподдерживаемый размер страницы сбрасывается к безопасному значению 12."""

    for index in range(13):
        make_product(
            category,
            name=f"Fallback Page Product {index}",
            slug=f"fallback-page-product-{index}",
            sku=f"SKU-FALLBACK-PAGE-{index}",
        )

    response = client.get(reverse("catalog:product_list"), {"per_page": "1000"})

    assert response.status_code == 200
    assert response.context["is_paginated"] is True
    assert len(response.context["products"]) == 12
    assert response.context["filter_state"]["per_page"] == "12"


def test_product_detail_opens_public_product(client, product):
    """Детальная страница открывает активный неудалённый товар из активной категории."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert_response_contains(response, product.name)
    assert_response_contains(response, product.description)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("is_active", False),
        ("is_deleted", True),
    ],
)
def test_product_detail_hides_non_public_product(client, category, field: str, value: bool):
    """Детальная страница не открывает неактивный или soft-deleted товар."""

    product = make_product(
        category,
        "Hidden Product",
        "hidden-product",
        "SKU-HIDDEN-PRODUCT",
        **{field: value},
    )

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 404


def test_product_detail_hides_product_from_hidden_category(client, product):
    """Товар из скрытой категории недоступен, даже если сам товар активен."""

    product.category.is_active = False
    product.category.save(update_fields=["is_active"])

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 404


def test_product_detail_uses_main_product_image(client, product):
    """Основное изображение берётся только из ProductImage и выбирается по is_main."""

    secondary_image = baker.make(
        "catalog.ProductImage",
        product=product,
        image="products/secondary.jpg",
        alt_text="Вторичное изображение",
        is_main=False,
        sort_order=1,
    )
    main_image = baker.make(
        "catalog.ProductImage",
        product=product,
        image="products/main.jpg",
        alt_text="Главное изображение",
        is_main=True,
        sort_order=2,
    )

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["main_image"] == main_image
    assert response.context["main_image"] != secondary_image
    assert_response_contains(response, "Главное изображение")


def test_product_detail_handles_product_without_images(client, product):
    """Отсутствие ProductImage не ломает страницу и отображается как штатное состояние."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["main_image"] is None
    assert_response_contains(response, "Изображение отсутствует")


def test_product_detail_shows_cart_form_for_available_product(client, product):
    """На этапе 8 доступный товар можно добавить в корзину через POST-форму."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Добавить в корзину" in content
    assert 'method="post"' in content.lower()
    assert reverse("cart:add", kwargs={"product_id": product.id}) in content


def test_product_detail_shows_out_of_stock_state(client, product):
    """Если остаток равен нулю, детальная страница показывает состояние отсутствия товара."""

    product.stock_quantity = 0
    product.save(update_fields=["stock_quantity"])

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert_response_contains(response, "Нет в наличии")


def test_product_detail_shows_only_published_reviews_and_rating(client, product, user, second_user):
    """Отзывы и рейтинг считаются только по опубликованным отзывам."""

    published_review = baker.make(
        "reviews.Review",
        user=user,
        product=product,
        rating=5,
        title="Публичный отзыв",
        text="Этот отзыв должен быть виден.",
        status=Review.Status.PUBLISHED,
    )
    hidden_review = baker.make(
        "reviews.Review",
        user=second_user,
        product=product,
        rating=1,
        title="Скрытый отзыв",
        text="Этот отзыв не должен быть виден.",
        status=Review.Status.HIDDEN,
    )

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert list(response.context["reviews"]) == [published_review]
    assert response.context["reviews_count"] == 1
    assert response.context["average_rating"] == 5
    assert_response_contains(response, published_review.title)
    assert_response_not_contains(response, hidden_review.title)


def test_product_detail_shows_empty_reviews_state(client, product):
    """Если опубликованных отзывов нет, страница показывает понятное пустое состояние."""

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["reviews_count"] == 0
    assert_response_contains(response, "Отзывов пока нет")


def test_product_detail_shows_related_products_from_same_public_category(client, category, product):
    """Похожие товары выбираются из той же активной категории и не включают текущий товар."""

    related_products = [make_product(category, f"Related Product {index}", f"related-product-{index}", f"SKU-RELATED-{index}") for index in range(4)]
    make_product(category, "Inactive Related", "inactive-related", "SKU-INACTIVE-RELATED", is_active=False)
    make_product(category, "Deleted Related", "deleted-related", "SKU-DELETED-RELATED", is_deleted=True)

    other_category = baker.make("catalog.Category", name="Other Category", slug="other-category")
    make_product(other_category, "Other Category Product", "other-category-product", "SKU-OTHER-CATEGORY")

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
    shown_related_products = list(response.context["related_products"])

    assert response.status_code == 200
    assert len(shown_related_products) == 3
    assert product not in shown_related_products
    assert shown_related_products == sorted(related_products, key=lambda item: item.name)[:3]
    assert_response_contains(response, "Related Product 0")
    assert_response_not_contains(response, "Inactive Related")
    assert_response_not_contains(response, "Deleted Related")
    assert_response_not_contains(response, "Other Category Product")


def test_product_detail_can_show_out_of_stock_related_product(client, category, product):
    """Похожий товар с нулевым остатком остаётся видимым, но помечается как отсутствующий."""

    related_product = make_product(
        category,
        "Out Of Stock Related",
        "out-of-stock-related",
        "SKU-OUT-RELATED",
        stock_quantity=0,
    )

    response = client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert related_product in response.context["related_products"]
    assert_response_contains(response, related_product.name)
    assert_response_contains(response, "Нет в наличии")
