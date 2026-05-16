from django.views.generic import ListView

from apps.catalog.filters import (
    SORT_OPTIONS,
    apply_product_filters,
    get_catalog_filter_state,
)
from apps.catalog.selectors import (
    get_active_category_queryset,
    get_product_list_queryset,
)


class HomeView(ListView):
    """
    Главная страница магазина.

    На текущем этапе она показывает короткую витрину активных товаров и ссылку
    на полный каталог. Детальная карточка товара появится на следующем этапе.
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
