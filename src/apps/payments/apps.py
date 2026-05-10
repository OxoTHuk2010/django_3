from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Конфигурация приложения payments.

    Приложение отвечает за платёжную часть проекта:
    - фиксацию попыток оплаты;
    - хранение статусов платежей;
    - хранение внешних идентификаторов платёжных провайдеров;
    - подготовку к будущей интеграции с платёжными шлюзами.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payments"
    verbose_name = "Платежи"
