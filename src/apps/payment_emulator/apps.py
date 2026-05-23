from django.apps import AppConfig


class PaymentEmulatorConfig(AppConfig):
    """Конфигурация приложения эмулятора платёжного провайдера."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payment_emulator"
    verbose_name = "Эмулятор оплаты"
