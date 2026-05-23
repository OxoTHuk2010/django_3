from django.contrib import admin
from django.urls import reverse

from apps.common.analytics import get_admin_dashboard_analytics

admin.site.site_header = "MyShop Admin"
admin.site.site_title = "MyShop Admin"
admin.site.index_title = "Панель управления MyShop"

_original_admin_index = admin.site.index


def analytics_admin_index(request, extra_context=None):
    """Добавить аналитику в стандартный admin index без замены Django Admin."""

    context = dict(extra_context or {})
    context["analytics"] = add_admin_urls_to_analytics(get_admin_dashboard_analytics(request.GET.get("period")))
    return _original_admin_index(request, extra_context=context)


admin.site.index = analytics_admin_index


def add_admin_urls_to_analytics(analytics):
    """Добавить admin-ссылки на объекты перед передачей данных в шаблон."""

    for product in analytics["low_stock_products"]:
        product["admin_url"] = reverse("admin:catalog_product_change", args=[product["id"]])

    for product in analytics["top_products"]:
        product["admin_url"] = reverse("admin:catalog_product_change", args=[product["product_id"]])

    for review in analytics["pending_reviews"]:
        review["admin_url"] = reverse("admin:reviews_review_change", args=[review["id"]])

    return analytics
