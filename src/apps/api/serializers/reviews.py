from rest_framework import serializers

from apps.reviews.models import Review


class ReviewAuthorSerializer(serializers.Serializer):
    """Публичный автор отзыва."""

    id = serializers.IntegerField()
    username = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    """Публичное представление опубликованного или созданного отзыва."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "id",
            "rating",
            "title",
            "text",
            "status",
            "is_verified_purchase",
            "author",
            "created_at",
            "updated_at",
        )

    def get_author(self, obj: Review) -> dict:
        """Вернуть безопасные публичные данные автора."""

        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }


class ReviewCreateSerializer(serializers.Serializer):
    """Payload создания отзыва через API."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    text = serializers.CharField(allow_blank=False)
