from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """
    Пользователь системы.

    Основной логин:
        username

    Email:
        вспомогательное контактное поле.

    Почему не email как логин:
        На текущем этапе проекта используется стандартная модель
        аутентификации Django через username/password.

        Это упрощает:
        - создание суперпользователя;
        - вход в Django Admin;
        - получение JWT-токена;
        - сопровождение проекта;
        - тестирование.
    """

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="Email",
        help_text="Уникальный email пользователя.",
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """
        Строковое представление пользователя.

        Используется в Django admin, логах и связанных моделях.
        """

        return self.username
