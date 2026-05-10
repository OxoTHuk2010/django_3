from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """
    Конфигурация приложения catalog.

    Приложение отвечает за товарный каталог:
    - категории;
    - товары;
    - изображения товаров.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Каталог"
