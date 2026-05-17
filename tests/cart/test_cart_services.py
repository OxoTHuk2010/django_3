from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from model_bakery import baker

from apps.cart.models import CartItem
from apps.cart.services import (
    MAX_CART_ITEM_QUANTITY,
    SESSION_CART_KEY,
    add_to_cart,
    clear_cart,
    get_cart_snapshot,
    merge_session_cart_to_user_cart,
    remove_from_cart,
    update_cart_item,
)

pytestmark = pytest.mark.django_db


def make_request(user=None):
    """Создать request с рабочей session для прямой проверки сервисного слоя."""

    request = RequestFactory().get("/cart/")
    middleware = SessionMiddleware(lambda current_request: None)
    middleware.process_request(request)
    request.session.save()
    request.user = user if user is not None else AnonymousUser()
    return request


def make_public_product(category, **kwargs):
    """Создать публичный товар с безопасными значениями по умолчанию."""

    defaults = {
        "category": category,
        "name": "Service Product",
        "slug": "service-product",
        "sku": "SKU-SERVICE",
        "price": Decimal("100.00"),
        "stock_quantity": 10,
        "is_active": True,
        "is_deleted": False,
    }
    defaults.update(kwargs)
    return baker.make("catalog.Product", **defaults)


def test_add_to_cart_creates_guest_session_item(product):
    """Гость добавляет товар в session-cart без создания DB-корзины."""

    request = make_request()

    result = add_to_cart(request, product, 2)

    assert result.success is True
    assert request.session[SESSION_CART_KEY] == {str(product.id): 2}
    assert result.snapshot.total_quantity == 2


def test_add_to_cart_increments_existing_guest_item(product):
    """Повторное добавление товара увеличивает количество существующей позиции."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {str(product.id): 2}

    result = add_to_cart(request, product, 3)

    assert result.success is True
    assert request.session[SESSION_CART_KEY][str(product.id)] == 5


def test_update_cart_item_replaces_guest_quantity(product):
    """Изменение количества заменяет старое значение, а не складывает его."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {str(product.id): 2}

    result = update_cart_item(request, product, 4)

    assert result.success is True
    assert request.session[SESSION_CART_KEY][str(product.id)] == 4


def test_remove_from_cart_deletes_guest_item(product):
    """Удаление товара убирает позицию из session-cart."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {str(product.id): 2}

    result = remove_from_cart(request, product)

    assert result.success is True
    assert SESSION_CART_KEY not in request.session


def test_clear_cart_removes_all_guest_items(product):
    """Очистка корзины удаляет все позиции гостя."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {str(product.id): 2}

    result = clear_cart(request)

    assert result.success is True
    assert SESSION_CART_KEY not in request.session


def test_add_to_cart_rejects_quantity_over_stock(product):
    """Нельзя добавить больше товара, чем доступно на складе."""

    request = make_request()

    result = add_to_cart(request, product, product.stock_quantity + 1)

    assert result.success is False
    assert result.errors == ["quantity_gt_stock"]
    assert SESSION_CART_KEY not in request.session


def test_add_to_cart_rejects_quantity_over_system_limit(product):
    """Нельзя добавить количество больше системного лимита позиции."""

    request = make_request()
    product.stock_quantity = MAX_CART_ITEM_QUANTITY + 10
    product.save(update_fields=["stock_quantity"])

    result = add_to_cart(request, product, MAX_CART_ITEM_QUANTITY + 1)

    assert result.success is False
    assert result.errors == ["quantity_gt_max"]
    assert SESSION_CART_KEY not in request.session


def test_add_to_cart_rejects_hidden_product(product):
    """Сервис не добавляет неактивный товар и не меняет корзину."""

    request = make_request()
    product.is_active = False
    product.save(update_fields=["is_active"])

    result = add_to_cart(request, product, 1)

    assert result.success is False
    assert result.errors == ["product_unavailable"]
    assert SESSION_CART_KEY not in request.session


def test_get_cart_snapshot_removes_broken_guest_items(product):
    """Snapshot удаляет битые product_id и оставляет только валидные позиции."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {
        str(product.id): 2,
        "999999": 1,
        "bad-id": 3,
    }

    snapshot = get_cart_snapshot(request)

    assert snapshot.total_quantity == 2
    assert snapshot.warnings
    assert request.session[SESSION_CART_KEY] == {str(product.id): 2}


def test_get_cart_snapshot_keeps_out_of_stock_item(product):
    """Товар без остатка остаётся в корзине, но блокирует checkout."""

    request = make_request()
    product.stock_quantity = 0
    product.save(update_fields=["stock_quantity"])
    request.session[SESSION_CART_KEY] = {str(product.id): 1}

    snapshot = get_cart_snapshot(request)

    assert snapshot.is_empty is False
    assert snapshot.can_checkout is False
    assert snapshot.has_unavailable_items is True
    assert snapshot.items[0].is_available is False


def test_get_cart_snapshot_does_not_clip_quantity_over_stock(product):
    """Snapshot не обрезает quantity silently, если остаток стал меньше."""

    request = make_request()
    product.stock_quantity = 1
    product.save(update_fields=["stock_quantity"])
    request.session[SESSION_CART_KEY] = {str(product.id): 3}

    snapshot = get_cart_snapshot(request)

    assert request.session[SESSION_CART_KEY][str(product.id)] == 3
    assert snapshot.can_checkout is False
    assert snapshot.warnings


def test_add_to_cart_creates_db_cart_for_authenticated_user(user, product):
    """Авторизованный пользователь добавляет товар в постоянную DB-корзину."""

    request = make_request(user=user)

    result = add_to_cart(request, product, 2)

    assert result.success is True
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 2
    assert SESSION_CART_KEY not in request.session


def test_update_cart_item_replaces_db_quantity(user, cart, product):
    """Изменение количества в DB-корзине заменяет старое значение."""

    request = make_request(user=user)
    baker.make("cart.CartItem", cart=cart, product=product, quantity=2)

    result = update_cart_item(request, product, 5)

    assert result.success is True
    assert CartItem.objects.get(cart=cart, product=product).quantity == 5


def test_merge_session_cart_to_user_cart_caps_quantity(user, cart, product):
    """Merge складывает количества и ограничивает итог остатком и системным лимитом."""

    request = make_request()
    request.session[SESSION_CART_KEY] = {str(product.id): 5}
    baker.make("cart.CartItem", cart=cart, product=product, quantity=8)

    result = merge_session_cart_to_user_cart(request, user)

    assert result.success is True
    assert CartItem.objects.get(cart=cart, product=product).quantity == 10
    assert SESSION_CART_KEY not in request.session


def test_merge_session_cart_skips_unavailable_products(user, cart, category):
    """Merge пропускает товары, которые нельзя использовать для покупки."""

    request = make_request()
    inactive_product = make_public_product(
        category,
        name="Inactive",
        slug="inactive",
        sku="SKU-INACTIVE-MERGE",
        is_active=False,
    )
    request.session[SESSION_CART_KEY] = {str(inactive_product.id): 1}

    result = merge_session_cart_to_user_cart(request, user)

    assert result.success is True
    assert cart.items.count() == 0
    assert SESSION_CART_KEY not in request.session
