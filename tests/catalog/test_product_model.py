from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_product_can_be_created(product):
    """Товар создаётся с ключевыми полями каталога и человекочитаемым __str__."""
    assert product.id is not None
    assert product.name == "ThinkPad X1 Carbon"
    assert product.slug == "thinkpad-x1-carbon"
    assert product.sku == "SKU-THINKPAD-X1"
    assert str(product) == product.name


def test_product_is_available_when_active_not_deleted_and_in_stock(product):
    """Товар доступен к покупке только при активном состоянии, отсутствии soft delete и положительном остатке."""
    assert product.is_available is True


@pytest.mark.parametrize(
    ("is_active", "is_deleted", "stock_quantity"),
    [
        (False, False, 10),
        (True, True, 10),
        (True, False, 0),
    ],
)
def test_product_is_not_available_when_state_or_stock_blocks_purchase(product, is_active, is_deleted, stock_quantity):
    """Любой блокирующий признак делает товар недоступным для покупки."""
    product.is_active = is_active
    product.is_deleted = is_deleted
    product.stock_quantity = stock_quantity

    assert product.is_available is False


def test_product_slug_is_unique(product, category):
    """Slug товара уникален, чтобы детальная страница товара однозначно определялась URL."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make(
                "catalog.Product",
                category=category,
                name="Duplicate slug",
                slug=product.slug,
                sku="SKU-DIFFERENT",
                price=Decimal("100.00"),
                stock_quantity=1,
            )


def test_product_sku_is_unique(product, category):
    """SKU товара уникален как внутренний артикул каталога."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make(
                "catalog.Product",
                category=category,
                name="Duplicate sku",
                slug="duplicate-sku",
                sku=product.sku,
                price=Decimal("100.00"),
                stock_quantity=1,
            )


@pytest.mark.parametrize(
    ("field", "value", "constraint"),
    [
        ("price", Decimal("-1.00"), "catalog_product_price_gte_0"),
        ("old_price", Decimal("-1.00"), "catalog_product_old_price_gte_0"),
        ("stock_quantity", -1, "catalog_product_stock_gte_0"),
    ],
)
def test_product_non_negative_constraints(product, field, value, constraint):
    """База данных защищает цену, старую цену и остаток от отрицательных значений."""
    setattr(product, field, value)

    with pytest.raises(IntegrityError, match=constraint):
        with transaction.atomic():
            product.save(update_fields=[field])


def test_product_soft_delete_and_restore(product):
    """Soft delete скрывает товар из доступных к покупке и допускает восстановление."""
    product.soft_delete()
    product.refresh_from_db()

    assert product.is_deleted is True
    assert product.deleted_at is not None
    assert product.is_available is False

    product.restore()
    product.refresh_from_db()

    assert product.is_deleted is False
    assert product.deleted_at is None
