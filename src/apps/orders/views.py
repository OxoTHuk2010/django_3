from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormView

from apps.cart.services import clear_cart, get_cart_snapshot
from apps.orders.forms import CheckoutForm
from apps.orders.services import CheckoutError, create_order_from_cart


class CheckoutView(LoginRequiredMixin, FormView):
    """Страница оформления заказа для авторизованного пользователя."""

    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def dispatch(self, request, *args, **kwargs):
        """Не пускать пользователя в checkout с пустой или невалидной корзиной."""

        self.cart_snapshot = get_cart_snapshot(request)
        if not self.cart_snapshot.can_checkout:
            messages.error(request, "Корзина пуста или содержит товары, недоступные для оформления.")
            return redirect("cart:detail")

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Предзаполнить checkout данными текущего пользователя, если они есть."""

        initial = super().get_initial()
        user = self.request.user
        full_name = user.get_full_name().strip()
        initial.update(
            {
                "customer_name": full_name or user.username,
                "customer_email": user.email or "",
                "customer_phone": getattr(user, "phone", ""),
            },
        )
        return initial

    def get_context_data(self, **kwargs):
        """Добавить snapshot корзины в шаблон подтверждения заказа."""

        context = super().get_context_data(**kwargs)
        context["cart_snapshot"] = self.cart_snapshot
        return context

    def form_valid(self, form):
        """Создать заказ и очистить корзину только после успешной транзакции."""

        try:
            checkout_result = create_order_from_cart(
                user=self.request.user,
                cart_snapshot=self.cart_snapshot,
                shipping_data=form.cleaned_data,
            )
        except CheckoutError as error:
            messages.error(self.request, str(error))
            return redirect("cart:detail")

        if checkout_result.should_clear_cart:
            clear_cart(self.request)
            messages.success(self.request, f"Заказ #{checkout_result.order.id} успешно оформлен и оплачен.")
        else:
            messages.warning(
                self.request,
                "Заказ создан, но оплата не завершена. Корзина сохранена для повторной попытки.",
            )
        return redirect("users:order_detail", pk=checkout_result.order.pk)

    def get_success_url(self):
        """Формально требуется FormView, фактический redirect выполняется в form_valid."""

        return reverse("cart:detail")
