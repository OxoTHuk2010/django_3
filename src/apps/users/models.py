from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """
    Кастомная модель пользователя интернет-магазина.

    Почему используется кастомная модель:
    - стандартную модель User сложно заменить после первых миграций;
    - почти в любом реальном проекте появляются дополнительные поля;
    - проще заранее заложить возможность развития модели пользователя.

    На текущем этапе пользователь авторизуется по email.
    Поле username оставлено для совместимости с Django admin и AbstractUser.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Уникальный email пользователя. Используется для входа в систему.",
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Телефон",
        help_text="Контактный телефон пользователя.",
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя",
        help_text="Имя пользователя.",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия",
        help_text="Фамилия пользователя.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = [
            "email",
        ]
        indexes = [
            models.Index(
                fields=[
                    "email",
                ],
                name="users_user_email_idx",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление пользователя.

        Используется в Django admin, логах и связанных моделях.
        """

        return self.email
