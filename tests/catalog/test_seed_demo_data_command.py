import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.catalog.models import Category, Product
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_seed_demo_data_is_idempotent():
    """Повторный запуск seed-команды не создаёт дубликаты demo-данных."""

    call_command("seed_demo_data")
    first_counts = _demo_counts()

    call_command("seed_demo_data")
    second_counts = _demo_counts()

    assert first_counts == second_counts
    assert first_counts["users"] == 2
    assert first_counts["categories"] == 3
    assert first_counts["products"] == 5
    assert first_counts["orders"] == 2
    assert first_counts["reviews"] == 2


def test_seed_demo_data_reset_requires_yes():
    """Destructive reset запрещён без явного подтверждения `--yes`."""

    with pytest.raises(CommandError, match="without --yes"):
        call_command("seed_demo_data", reset=True)


@override_settings(DEBUG=False)
def test_seed_demo_data_reset_is_blocked_when_debug_false():
    """Destructive reset запрещён при DEBUG=False."""

    with pytest.raises(CommandError, match="DEBUG=False"):
        call_command("seed_demo_data", reset=True, yes=True)


def _demo_counts() -> dict[str, int]:
    """Посчитать только известные demo-записи по стабильным ключам."""

    demo_usernames = ["demo_customer", "demo_reviewer"]
    demo_category_slugs = ["malt", "hops", "yeast"]
    demo_product_slugs = [
        "pilsner-malt",
        "caramel-malt",
        "cascade-hops",
        "citra-hops",
        "safale-us05-yeast",
    ]
    demo_users = User.objects.filter(username__in=demo_usernames)

    return {
        "users": demo_users.count(),
        "categories": Category.objects.filter(slug__in=demo_category_slugs).count(),
        "products": Product.objects.filter(slug__in=demo_product_slugs).count(),
        "orders": Order.objects.filter(user__in=demo_users).count(),
        "reviews": Review.objects.filter(user__in=demo_users).count(),
    }
