from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.users.models import User


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя через стандартный username/password."""

    email = forms.EmailField(
        label="Email",
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
        )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования базовых профильных данных пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
        )
