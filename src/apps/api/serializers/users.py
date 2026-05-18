from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class UserSummarySerializer(serializers.ModelSerializer):
    """Краткое представление пользователя для API."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class UserRegistrationSerializer(serializers.Serializer):
    """Payload API-регистрации с выдачей JWT pair."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_username(self, value: str) -> str:
        """Проверить уникальность username."""

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

    def validate_email(self, value: str) -> str:
        """Проверить обязательность и уникальность email для API-регистрации."""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_password(self, value: str) -> str:
        """Применить стандартные Django validators к паролю."""

        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        """Создать пользователя с безопасным хешированием пароля."""

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance: User) -> dict:
        """Вернуть пользователя и JWT pair после успешной регистрации."""

        refresh = RefreshToken.for_user(instance)
        return {
            "user": UserSummarySerializer(instance).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }
