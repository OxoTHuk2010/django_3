from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Конфигурация приложения orders.

    Приложение отвечает за оформление и хранение заказов:
    - заказ;
    - позиции заказа;
    - статус заказа.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    verbose_name = "Заказы"
