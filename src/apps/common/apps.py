from django.apps import AppConfig


class CommonConfig(AppConfig):
    """
    Конфигурация приложения common.

    Приложение хранит общие базовые классы, миксины и утилиты,
    которые используются в других доменных приложениях проекта.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    verbose_name = "Общее"
