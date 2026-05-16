from django.db.models import QuerySet

from apps.catalog.models import Category, Product


def get_active_category_queryset() -> QuerySet[Category]:
    """
    Вернуть категории, доступные для публичного каталога.

    Публичный каталог не должен показывать неактивные категории и категории,
    скрытые через soft delete.
    """

    return Category.objects.filter(
        is_active=True,
        is_deleted=False,
    ).order_by("name")


def get_product_list_queryset() -> QuerySet[Product]:
    """
    Вернуть базовый queryset товаров для публичного списка.

    Здесь фиксируется общее правило видимости: пользователь видит только
    активные неудалённые товары из активных неудалённых категорий.
    """

    return (
        Product.objects.filter(
            is_active=True,
            is_deleted=False,
            category__is_active=True,
            category__is_deleted=False,
        )
        .select_related("category")
        .prefetch_related("images")
    )
