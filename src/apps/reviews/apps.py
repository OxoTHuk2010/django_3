from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """
    Конфигурация приложения reviews.

    Приложение отвечает за пользовательские отзывы о товарах:
    - рейтинг;
    - текст отзыва;
    - модерацию;
    - публикацию;
    - связь пользователя с товаром.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"
    verbose_name = "Отзывы"
