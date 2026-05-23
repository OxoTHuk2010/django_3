from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.reviews.models import Review


@dataclass(frozen=True)
class AnalyticsPeriod:
    """Период, по которому считаются временные метрики аналитики."""

    key: str
    label: str
    start_at: datetime | None
    end_at: datetime


PERIOD_OPTIONS = (
    ("today", "Сегодня"),
    ("7d", "7 дней"),
    ("30d", "30 дней"),
    ("all", "Всё время"),
)

MONEY_QUANT = Decimal("0.01")

PAID_ORDER_STATUSES = (
    Order.Status.PAID,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.COMPLETED,
)


def resolve_analytics_period(period_key: str | None, *, now: datetime | None = None) -> AnalyticsPeriod:
    """Нормализовать GET-параметр периода в явные границы времени."""

    current_time = now or timezone.now()
    normalized_key = period_key if period_key in dict(PERIOD_OPTIONS) else "30d"

    if normalized_key == "today":
        start_at = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif normalized_key == "7d":
        start_at = current_time - timedelta(days=7)
    elif normalized_key == "30d":
        start_at = current_time - timedelta(days=30)
    else:
        start_at = None

    return AnalyticsPeriod(
        key=normalized_key,
        label=dict(PERIOD_OPTIONS)[normalized_key],
        start_at=start_at,
        end_at=current_time,
    )


def filter_by_period(queryset, period: AnalyticsPeriod, field_name: str = "created_at"):
    """Применить период к queryset без дублирования фильтров в admin и будущем GraphQL."""

    if period.start_at is None:
        return queryset

    return queryset.filter(
        **{
            f"{field_name}__gte": period.start_at,
            f"{field_name}__lte": period.end_at,
        }
    )


def get_admin_dashboard_analytics(period_key: str | None = None) -> dict[str, Any]:
    """Собрать метрики для staff dashboard через общий read/service слой."""

    period = resolve_analytics_period(period_key)
    orders = filter_by_period(Order.objects.all(), period)
    payments = filter_by_period(Payment.objects.all(), period)
    users = filter_by_period(get_user_model().objects.all(), period, "date_joined")
    order_items = filter_by_period(OrderItem.objects.select_related("product", "order"), period, "order__created_at")
    reviews = filter_by_period(Review.objects.select_related("product", "user"), period)

    succeeded_payments = payments.filter(status=Payment.Status.SUCCEEDED)
    paid_orders = orders.filter(status__in=PAID_ORDER_STATUSES)
    pending_payments = payments.filter(status=Payment.Status.PENDING)
    failed_payments = payments.filter(status=Payment.Status.FAILED)
    pending_reviews = reviews.filter(status=Review.Status.PENDING)

    revenue = succeeded_payments.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
    paid_orders_total = paid_orders.aggregate(total=Coalesce(Sum("total_price"), Decimal("0.00")))["total"]
    paid_orders_count = paid_orders.count()
    average_order_value = (paid_orders_total / paid_orders_count).quantize(MONEY_QUANT) if paid_orders_count else Decimal("0.00")

    return {
        "period": {
            "key": period.key,
            "label": period.label,
            "options": PERIOD_OPTIONS,
        },
        "summary": {
            "revenue": revenue,
            "orders_count": orders.count(),
            "average_order_value": average_order_value,
            "new_users_count": users.count(),
            "paid_orders_count": paid_orders_count,
            "pending_payments_count": pending_payments.count(),
            "failed_payments_count": failed_payments.count(),
        },
        "low_stock_products": list(_get_low_stock_products()),
        "top_products": list(_get_top_products(order_items)),
        "pending_reviews": list(_get_pending_reviews(pending_reviews)),
    }


def _get_low_stock_products(limit: int = 5, threshold: int = 5):
    """Вернуть текущие товары с низким остатком независимо от выбранного периода."""

    return (
        Product.objects.filter(is_active=True, is_deleted=False, stock_quantity__lte=threshold)
        .order_by("stock_quantity", "name")
        .values(
            "id",
            "name",
            "sku",
            "stock_quantity",
        )[:limit]
    )


def _get_top_products(order_items, limit: int = 5):
    """Вернуть товары с максимальным количеством проданных единиц за период."""

    return (
        order_items.filter(order__status__in=PAID_ORDER_STATUSES)
        .values(
            "product_id",
            "product__name",
        )
        .annotate(
            sold_quantity=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(F("quantity") * F("price")), Decimal("0.00")),
        )
        .order_by("-sold_quantity", "product__name")[:limit]
    )


def _get_pending_reviews(pending_reviews, limit: int = 5):
    """Вернуть последние отзывы, ожидающие модерации."""

    return pending_reviews.order_by("-created_at").values(
        "id",
        "product__name",
        "user__username",
        "rating",
        "created_at",
    )[:limit]
