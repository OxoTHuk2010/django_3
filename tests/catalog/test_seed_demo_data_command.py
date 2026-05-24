import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils.crypto import get_random_string

from apps.catalog.models import Category, Product, ProductImage
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.users.models import User

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_seed_demo_data_is_idempotent():
    """Повторный запуск seed-команды не создаёт дубликаты demo-данных."""

    call_command("seed_demo_data")
    first_counts = _demo_counts()

    call_command("seed_demo_data")
    second_counts = _demo_counts()

    assert first_counts == second_counts
    assert first_counts["users"] == 4
    assert first_counts["categories"] == 5
    assert first_counts["products"] == 12
    assert first_counts["product_images"] == 12
    assert first_counts["orders"] == 4
    assert first_counts["reviews"] == 36


@override_settings(DEBUG=True)
def test_seed_demo_data_creates_unusable_passwords_without_env(monkeypatch):
    """Без env-пароля demo-пользователь создаётся без пригодного для входа пароля."""

    monkeypatch.delenv("MYSHOP_DEMO_PASSWORD", raising=False)

    call_command("seed_demo_data")

    user = User.objects.get(username="demo_customer")
    assert not user.has_usable_password()


@override_settings(DEBUG=True)
def test_seed_demo_data_uses_password_from_env(monkeypatch):
    """Demo-пароль берётся только из env, а не из кода репозитория."""

    demo_password = f"runtime-only-{get_random_string(24)}"
    monkeypatch.setenv("MYSHOP_DEMO_PASSWORD", demo_password)

    call_command("seed_demo_data")

    user = User.objects.get(username="demo_customer")
    assert user.check_password(demo_password)


@override_settings(DEBUG=False)
def test_seed_demo_data_is_blocked_when_debug_false():
    """Создание demo-аккаунтов запрещено в production-like режиме."""

    with pytest.raises(CommandError, match="outside local/demo environment"):
        call_command("seed_demo_data")


@override_settings(DEBUG=True)
def test_seed_demo_data_reset_requires_yes():
    """Destructive reset запрещён без явного подтверждения `--yes`."""

    with pytest.raises(CommandError, match="without --yes"):
        call_command("seed_demo_data", reset=True)


@override_settings(DEBUG=False)
def test_seed_demo_data_reset_is_blocked_when_debug_false():
    """Destructive reset запрещён при DEBUG=False."""

    with pytest.raises(CommandError, match="outside local/demo environment"):
        call_command("seed_demo_data", reset=True, yes=True)


def _demo_counts() -> dict[str, int]:
    """Посчитать только известные demo-записи по стабильным ключам."""

    demo_usernames = ["demo_customer", "demo_reviewer", "demo_brewer", "demo_taster"]
    demo_category_slugs = ["malt", "hops", "yeast", "adjuncts", "kits"]
    demo_product_slugs = [
        "pilsner-malt",
        "caramel-malt",
        "maris-otter-malt",
        "cascade-hops",
        "citra-hops",
        "saaz-hops",
        "centennial-hops",
        "mosaic-hops",
        "safale-us05-yeast",
        "imperial-yeast",
        "west-coast-ipa-kit",
        "unmalted-wheat",
    ]
    demo_users = User.objects.filter(username__in=demo_usernames)
    demo_products = Product.objects.filter(slug__in=demo_product_slugs)

    return {
        "users": demo_users.count(),
        "categories": Category.objects.filter(slug__in=demo_category_slugs).count(),
        "products": demo_products.count(),
        "product_images": ProductImage.objects.filter(product__in=demo_products, image__startswith="demo/products/").count(),
        "orders": Order.objects.filter(user__in=demo_users).count(),
        "reviews": Review.objects.filter(user__in=demo_users).count(),
    }
