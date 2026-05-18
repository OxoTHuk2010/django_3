from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.exceptions import validation_error_response
from apps.api.serializers.users import UserRegistrationSerializer


class UserRegistrationAPIView(APIView):
    """API-регистрация пользователя с выдачей JWT pair."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Создать пользователя и вернуть данные пользователя с токенами."""

        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)

        user = serializer.save()
        return Response(serializer.to_representation(user), status=status.HTTP_201_CREATED)
