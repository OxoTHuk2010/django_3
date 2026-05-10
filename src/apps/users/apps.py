from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.

    Приложение отвечает за пользователей проекта.
    На старте используется кастомная модель пользователя,
    чтобы в будущем не упереться в ограничения стандартного auth.User.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Пользователи"
