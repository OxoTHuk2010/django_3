from decimal import Decimal, InvalidOperation
from typing import Any

from django.db.models import Count, Q, QuerySet
from django.http import QueryDict

from apps.catalog.models import Product

DEFAULT_SORT = "newest"

SORT_OPTIONS: dict[str, tuple[str, str]] = {
    "newest": ("-created_at", "Сначала новые"),
    "price_asc": ("price", "Сначала дешевле"),
    "price_desc": ("-price", "Сначала дороже"),
    "popular": ("popular", "Популярные"),
}


def apply_product_filters(queryset: QuerySet[Product], params: QueryDict | dict[str, Any]) -> QuerySet[Product]:
    """
    Применить фильтры публичного каталога к queryset товаров.

    Функция не создаёт базовый queryset сама: правила видимости товаров остаются
    в `selectors.py`, а здесь находятся только пользовательские фильтры.
    """

    query = str(params.get("q", "")).strip()
    category_slug = str(params.get("category", "")).strip()
    price_min = _parse_decimal(params.get("price_min"))
    price_max = _parse_decimal(params.get("price_max"))
    sort = _get_sort_key(params)

    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query))

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if price_min is not None:
        queryset = queryset.filter(price__gte=price_min)

    if price_max is not None:
        queryset = queryset.filter(price__lte=price_max)

    if sort == "popular":
        return queryset.annotate(orders_count=Count("order_items")).order_by("-orders_count", "name")

    sort_field = SORT_OPTIONS[sort][0]
    return queryset.order_by(sort_field, "name")


def get_catalog_filter_state(params: QueryDict | dict[str, Any]) -> dict[str, str]:
    """
    Подготовить текущее состояние фильтров для шаблона.

    Значения возвращаются строками, чтобы шаблон мог безопасно подставлять их
    обратно в форму фильтрации.
    """

    return {
        "q": str(params.get("q", "")).strip(),
        "category": str(params.get("category", "")).strip(),
        "price_min": str(params.get("price_min", "")).strip(),
        "price_max": str(params.get("price_max", "")).strip(),
        "sort": _get_sort_key(params),
    }


def _get_sort_key(params: QueryDict | dict[str, Any]) -> str:
    """
    Вернуть безопасный ключ сортировки.

    Неизвестные значения сортировки игнорируются, чтобы пользовательский GET
    параметр не мог напрямую управлять `order_by`.
    """

    sort = str(params.get("sort", DEFAULT_SORT)).strip()
    if sort in SORT_OPTIONS:
        return sort
    return DEFAULT_SORT


def _parse_decimal(value: object) -> Decimal | None:
    """
    Преобразовать значение цены из GET-параметра.

    Некорректные и отрицательные значения игнорируются: публичный каталог не
    должен падать из-за пользовательского ввода в фильтрах.
    """

    if value in (None, ""):
        return None

    try:
        parsed_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None

    if parsed_value < 0:
        return None

    return parsed_value
