from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.cart.forms import CartQuantityForm
from apps.cart.services import (
    add_to_cart,
    clear_cart,
    get_cart_snapshot,
    remove_from_cart,
    update_cart_item,
)
from apps.catalog.models import Product


class CartDetailView(TemplateView):
    """Страница текущей корзины пользователя или гостя."""

    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        """Добавить нормализованный snapshot корзины в шаблон."""

        context = super().get_context_data(**kwargs)
        context["cart_snapshot"] = get_cart_snapshot(self.request)
        return context


class CartProductActionView(View):
    """Базовый HTTP-слой для POST-действий над товаром в корзине."""

    form_class = CartQuantityForm

    def get_product(self, product_id: int) -> Product:
        """Найти товар по внутреннему идентификатору из cart URL."""

        return get_object_or_404(
            Product.objects.select_related("category"),
            pk=product_id,
        )

    def redirect_to_cart(self):
        """Вернуть пользователя на страницу корзины после POST-действия."""

        return redirect("cart:detail")

    def handle_result(self, request, result):
        """Преобразовать результат сервиса в flash-message и redirect."""

        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)

        return self.redirect_to_cart()


class CartAddView(CartProductActionView):
    """Добавить товар в корзину через POST."""

    def post(self, request, product_id: int):
        """Обработать POST-форму добавления товара."""

        product = self.get_product(product_id)
        form = self.form_class(request.POST)

        if not form.is_valid():
            messages.error(request, "Введите корректное количество товара.")
            return self.redirect_to_cart()

        result = add_to_cart(
            request=request,
            product=product,
            quantity=form.cleaned_data["quantity"],
        )
        return self.handle_result(request, result)


class CartUpdateView(CartProductActionView):
    """Изменить количество товара в корзине через POST."""

    def post(self, request, product_id: int):
        """Обработать POST-форму изменения количества."""

        product = self.get_product(product_id)
        form = self.form_class(request.POST)

        if not form.is_valid():
            messages.error(request, "Введите корректное количество товара.")
            return self.redirect_to_cart()

        result = update_cart_item(
            request=request,
            product=product,
            quantity=form.cleaned_data["quantity"],
        )
        return self.handle_result(request, result)


class CartRemoveView(CartProductActionView):
    """Удалить товар из корзины через POST."""

    def post(self, request, product_id: int):
        """Обработать удаление позиции корзины."""

        product = self.get_product(product_id)
        result = remove_from_cart(request=request, product=product)
        return self.handle_result(request, result)


class CartClearView(View):
    """Очистить корзину через POST."""

    def post(self, request):
        """Обработать очистку всей корзины."""

        result = clear_cart(request)
        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)

        return redirect("cart:detail")
