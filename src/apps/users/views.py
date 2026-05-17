from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from apps.cart.services import merge_session_cart_to_user_cart
from apps.orders.models import Order
from apps.users.forms import UserProfileForm, UserRegistrationForm


class UserRegisterView(CreateView):
    """Регистрация пользователя с автоматическим входом после создания аккаунта."""

    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        """Создать пользователя, выполнить вход и объединить гостевую корзину."""

        response = super().form_valid(form)
        login(self.request, self.object)
        merge_session_cart_to_user_cart(self.request, self.object)
        messages.success(self.request, "Регистрация завершена. Гостевая корзина объединена с аккаунтом.")
        return response


class UserLoginView(LoginView):
    """Вход пользователя с объединением гостевой корзины после успешной авторизации."""

    template_name = "users/login.html"

    def form_valid(self, form):
        """Выполнить стандартный вход и перенести session-cart в DB-корзину."""

        response = super().form_valid(form)
        merge_session_cart_to_user_cart(self.request, self.request.user)
        messages.success(self.request, "Вы вошли в аккаунт.")
        return response


class UserProfileView(LoginRequiredMixin, TemplateView):
    """Личный кабинет текущего пользователя."""

    template_name = "users/profile.html"


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование данных текущего пользователя."""

    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        """Пользователь может редактировать только собственный профиль."""

        return self.request.user

    def form_valid(self, form):
        """Показать сообщение после сохранения профиля."""

        messages.success(self.request, "Профиль обновлён.")
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Смена пароля текущего пользователя."""

    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        """Показать сообщение после успешной смены пароля."""

        messages.success(self.request, "Пароль изменён.")
        return super().form_valid(form)


class UserOrderListView(LoginRequiredMixin, ListView):
    """История заказов текущего пользователя."""

    model = Order
    template_name = "users/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        """Вернуть только заказы текущего пользователя."""

        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "payments").order_by("-created_at")


class UserOrderDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница заказа текущего пользователя."""

    model = Order
    template_name = "users/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        """Запретить доступ к чужим заказам через фильтр queryset."""

        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "payments")


def redirect_to_profile(request):
    """Короткий редирект для старта личного кабинета."""

    return redirect("users:profile")
