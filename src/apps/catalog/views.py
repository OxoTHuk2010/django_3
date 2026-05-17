from django.views.generic import DetailView, ListView

from apps.catalog.filters import (
    SORT_OPTIONS,
    apply_product_filters,
    get_catalog_filter_state,
)
from apps.catalog.selectors import (
    get_active_category_queryset,
    get_product_detail_queryset,
    get_product_list_queryset,
    get_product_main_image,
    get_product_review_stats,
    get_published_product_reviews,
    get_related_products,
)


class HomeView(ListView):
    """
    Главная страница магазина.

    На текущем этапе она показывает короткую витрину активных товаров и ссылку
    на полный каталог. Карточки товаров ведут на публичную детальную страницу.
    """

    template_name = "catalog/home.html"
    context_object_name = "products"

    def get_queryset(self):
        """Вернуть несколько последних товаров для витрины главной страницы."""

        return get_product_list_queryset().order_by("-created_at", "name")[:6]

    def get_context_data(self, **kwargs):
        """Добавить категории для навигации на главной странице."""

        context = super().get_context_data(**kwargs)
        context["categories"] = get_active_category_queryset()[:6]
        return context


class ProductListView(ListView):
    """
    Публичный список товаров.

    View отвечает только за HTTP-слой: базовый queryset берётся из selector,
    пользовательские фильтры применяются отдельной функцией.
    """

    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        """Вернуть товары с учётом поиска, фильтров и сортировки."""

        return apply_product_filters(
            queryset=get_product_list_queryset(),
            params=self.request.GET,
        )

    def get_context_data(self, **kwargs):
        """Добавить данные формы фильтрации и строку запроса для пагинации."""

        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context["categories"] = get_active_category_queryset()
        context["filter_state"] = get_catalog_filter_state(self.request.GET)
        context["sort_options"] = SORT_OPTIONS
        context["querystring_without_page"] = query_params.urlencode()
        return context


class ProductDetailView(DetailView):
    """
    Публичная детальная страница товара.

    View собирает данные через selectors, чтобы HTTP-слой не содержал бизнес-правила
    видимости товара, отзывов, изображений и похожих товаров.
    """

    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Вернуть только публично доступные товары для открытия по slug."""

        return get_product_detail_queryset()

    def get_context_data(self, **kwargs):
        """Добавить read-only данные детальной страницы согласно ADR этапа 7."""

        context = super().get_context_data(**kwargs)
        product = self.object
        review_stats = get_product_review_stats(product)

        context["main_image"] = get_product_main_image(product)
        context["reviews"] = get_published_product_reviews(product)
        context["average_rating"] = review_stats["average_rating"]
        context["reviews_count"] = review_stats["reviews_count"]
        context["related_products"] = get_related_products(product)
        return context
