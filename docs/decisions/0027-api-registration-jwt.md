# ADR 0027: Контракт API-регистрации и JWT после регистрации

## Статус

Принято.

## Актуальная сжатая версия

- API-регистрация создаёт пользователя и возвращает JWT pair.
- Основной login identifier остаётся `username`, как зафиксировано ADR 0007.
- Email обязателен для API-регистрации и должен быть уникальным, но не становится основным логином.
- После появления конфликта `C036` этап 27 должен добавить `POST /api/users/login/` как compatibility alias для получения JWT.
- Существующие SimpleJWT endpoints можно сохранять.
- Подробные примеры ниже являются историческим контрактным контекстом.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

В проекте уже принято решение, что основной логин пользователя — `username`.

Web-регистрация уже реализует браузерный сценарий:

```text
- создаёт пользователя;
- выполняет вход через Django session;
- объединяет гостевую session-cart с DB-cart пользователя.
```

JWT-инфраструктура уже подключена:

POST /api/token/
POST /api/token/refresh/

В docs/api.md предварительно указан endpoint:

POST /api/users/register/

Перед реализацией API-регистрации необходимо определить:

- какие поля принимает API-регистрация;
- возвращает ли API JWT сразу после регистрации;
- допускается ли пустой email;
- выполняется ли merge session-cart после API-регистрации;
- нужен ли отдельный API login endpoint;
- как обрабатывать уникальность username и email.

Главный риск: API-регистрация может случайно начать повторять web-регистрацию, включая session-login и merge-cart. Для JWT API это нежелательно, потому что API должен быть независим от браузерной session.

## Решение

Принимаем решение:

API-регистрация создаёт пользователя и сразу возвращает JWT access/refresh pair.

Канонический endpoint:

POST /api/users/register/

После успешной регистрации API возвращает:

201 Created

и JSON с данными пользователя и JWT pair.

API-регистрация:

- не выполняет Django session login;
- не создаёт browser session;
- не использует session-cart;
- не выполняет merge session-cart в DB-cart;
- не зависит от cookies;
- не требует CSRF как session-form сценарий;
- не заменяет SimpleJWT /api/token/.

Итоговое правило:

Web-регистрация работает через session и может выполнять merge web-корзины.
API-регистрация работает через JWT и не выполняет merge session-cart.
Payload регистрации

Минимальный payload API-регистрации:

{
  "username": "ivan",
  "email": "ivan@example.com",
  "password": "StrongPassword123"
}

Обязательные поля:

username
password

Поле:

email

на этапе MVP также считаем обязательным для API-регистрации.

Причина: email нужен для нормальной e-commerce-модели, будущих уведомлений, восстановления доступа и связи с заказами.

Даже если username является основным логином, email должен быть собран при регистрации.

Правила username

username является основным логином пользователя.

Правила:

- username обязателен;
- username должен быть уникальным;
- username не должен быть пустым;
- username должен проходить стандартную Django-валидацию;
- username используется для получения JWT через /api/token/.

Если username уже занят:

400 Bad Request

Пример:

{
  "username": [
    "Пользователь с таким именем уже существует."
  ]
}
Правила email

email обязателен для API-регистрации.

Правила:

- email должен быть передан;
- email должен быть валидным email-адресом;
- email должен быть уникальным, если в модели User или бизнес-правилах проекта email объявлен уникальным;
- email не используется как основной логин на текущем этапе.

Если email не передан:

400 Bad Request

Пример:

{
  "email": [
    "Это поле обязательно."
  ]
}

Если email уже используется:

400 Bad Request

Пример:

{
  "email": [
    "Пользователь с таким email уже существует."
  ]
}

Если в текущей модели User.email ещё не имеет уникальности на уровне БД, на этапе API всё равно нужно валидировать уникальность email на уровне serializer/service, либо оформить отдельный ADR о допустимости неуникального email.

Для текущего решения принимаем:

email в API-регистрации должен быть уникальным.
Правила password

password обязателен.

Правила:

- password не должен быть пустым;
- password должен проходить стандартные Django password validators;
- password не возвращается в response;
- password хранится только через set_password().

Если пароль не проходит проверку:

400 Bad Request

Пример:

{
  "password": [
    "Введённый пароль слишком короткий."
  ]
}
Response после успешной регистрации

После успешной регистрации API возвращает:

201 Created

Пример response:

{
  "user": {
    "id": 42,
    "username": "ivan",
    "email": "ivan@example.com"
  },
  "tokens": {
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>"
  }
}

В response не должны возвращаться:

- password;
- password hash;
- is_staff;
- is_superuser;
- user_permissions;
- groups;
- служебные поля безопасности.
JWT после регистрации

API-регистрация сразу возвращает JWT pair.

Причина:

Для API-клиента регистрация обычно является началом authenticated-сессии.

Это избавляет клиента от второго запроса на /api/token/ сразу после регистрации.

При этом стандартный login endpoint остаётся:

POST /api/token/

Он используется для последующих входов уже существующего пользователя.

API login endpoint

Отдельный endpoint вида:

POST /api/users/login/

на этапе MVP не создаём.

Для входа используется SimpleJWT endpoint:

POST /api/token/

Payload для входа соответствует основному логину проекта:

{
  "username": "ivan",
  "password": "StrongPassword123"
}

Refresh выполняется через:

POST /api/token/refresh/

Дополнительный alias /api/users/login/ может быть добавлен позже только отдельным решением, если появится необходимость скрыть SimpleJWT-контракт или расширить login response.

Связь API-регистрации с корзиной

API-регистрация не связана с web session-cart.

На этапе MVP:

POST /api/users/register/ не выполняет merge session-cart.

Причина:

API-корзина доступна только авторизованным пользователям и работает только с DB-cart.

Это согласуется с ADR 0025.

Если клиент хочет работать с корзиной через API, порядок такой:

1. Зарегистрироваться через POST /api/users/register/.
2. Получить access/refresh tokens.
3. Использовать access token для API-корзины.
4. Добавлять товары через /api/cart/items/.

API не переносит товары из browser session-cart.

Если пользователь до регистрации работал с web-корзиной как гость, merge выполняется только в web login/register flow, а не через JWT API.

Граница ответственности

API-код регистрации находится в:

apps/api

Например:

apps/api/views/users.py
apps/api/serializers/users.py

Создание пользователя должно использовать корректную доменную функцию или serializer create(), но обязательно соблюдать правила:

- password устанавливается через set_password();
- username валидируется;
- email валидируется;
- JWT создаётся после успешного создания пользователя;
- операция не создаёт session.
Последствия

Плюсы решения:

- API-регистрация удобна для клиентов: сразу возвращает JWT;
- API не зависит от browser session;
- API не смешивается с web-регистрацией;
- корзина API остаётся JWT-first;
- не нужен отдельный login endpoint поверх /api/token/;
- поведение легко описать в Swagger;
- легко тестировать регистрацию и выдачу токенов;
- username остаётся основным логином проекта.

Минусы решения:

- API-регистрация отличается от web-регистрации по поведению session-login;
- web session-cart не переносится при API-регистрации;
- email становится обязательным в API даже при username-login;
- если в будущем понадобится регистрация без email, потребуется пересмотр;
- если понадобится `/api/users/login/`, его нужно будет добавить отдельным решением.
Связанные документы / файлы / настройки
- docs/api.md
- docs/architecture.md
- docs/decisions/0007-username-user-login.md
- docs/decisions/0023-api-architecture-boundary.md
- docs/decisions/0025-api-cart-contract.md
- docs/conflicts.md
- docs/decisions/0027-api-registration-jwt.md
- apps/api/serializers/users.py
- apps/api/views/users.py
- apps/api/urls.py
- apps/api/tests/test_users_api.py
- apps/users/models.py
- apps/users/forms.py
- apps/users/tests/
- config/settings/base.py
Инварианты для реализации
1. POST /api/users/register/ создаёт нового пользователя.
2. API-регистрация требует username, email и password.
3. username является основным логином.
4. username должен быть уникальным.
5. email должен быть валидным и уникальным.
6. password проходит Django password validators.
7. password не возвращается в response.
8. После успешной регистрации API возвращает access и refresh JWT.
9. API-регистрация не выполняет Django session login.
10. API-регистрация не выполняет merge session-cart.
11. Для повторного входа используется POST /api/token/.
12. Отдельный /api/users/login/ на этапе MVP не создаётся.
13. API-регистрация находится в apps/api.
14. API-регистрация не должна создавать или менять корзину.
Пример serializer
# apps/api/serializers/users.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
Пример API view
# apps/api/views/users.py

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.serializers.users import UserRegisterSerializer


class UserRegisterAPIView(APIView):
    """
    API-регистрация пользователя.

    Создаёт пользователя и возвращает JWT pair.
    Не выполняет session-login и merge session-cart.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )
Пример URL
# apps/api/urls.py

from django.urls import path

from apps.api.views import users as user_views

app_name = "api"

urlpatterns = [
    path(
        "users/register/",
        user_views.UserRegisterAPIView.as_view(),
        name="user-register",
    ),
]
Пример успешного запроса
POST /api/users/register/
Content-Type: application/json
{
  "username": "ivan",
  "email": "ivan@example.com",
  "password": "StrongPassword123"
}

Ответ:

201 Created
{
  "user": {
    "id": 42,
    "username": "ivan",
    "email": "ivan@example.com"
  },
  "tokens": {
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>"
  }
}
Пример тестовых ожиданий
1. POST /api/users/register/ создаёт пользователя.
2. Успешная регистрация возвращает 201 Created.
3. Успешная регистрация возвращает access JWT.
4. Успешная регистрация возвращает refresh JWT.
5. Response не содержит password.
6. username обязателен.
7. email обязателен.
8. password обязателен.
9. username должен быть уникальным.
10. email должен быть уникальным.
11. password должен проходить Django password validators.
12. После API-регистрации не создаётся session-login.
13. После API-регистрации не выполняется merge session-cart.
14. /api/token/ остаётся основным login endpoint для существующих пользователей.
15. /api/users/login/ не создаётся на этапе MVP.
Примечание по будущему развитию

Если в будущем потребуется подтверждение email, регистрация может измениться.

Возможные будущие варианты:

- регистрация создаёт inactive user;
- JWT выдаётся только после подтверждения email;
- refresh token не выдаётся до активации;
- добавляется /api/users/verify-email/;
- добавляется /api/users/resend-verification/.

Такое изменение должно быть оформлено отдельным ADR, потому что оно меняет публичный API-контракт регистрации.

На этапе MVP действует правило:

API-регистрация создаёт активного пользователя и сразу возвращает JWT pair.
