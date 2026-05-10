from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Конфигурация приложения cart.

    Приложение отвечает за корзину пользователя:
    - сама корзина;
    - позиции корзины.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cart"
    verbose_name = "Корзина"
