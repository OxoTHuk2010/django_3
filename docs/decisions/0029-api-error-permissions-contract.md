# ADR 0029: Единый формат ошибок и permissions в REST API

## Статус

Принято.

## Актуальная сжатая версия

- API ошибки приводятся к единому JSON-формату `{code, detail, fields}`.
- Validation and business-rule errors use predictable HTTP status codes and machine-readable codes.
- Чужие приватные ресурсы, включая чужие заказы, скрываются через `404`.
- JWT auth failures return `401`; authenticated-but-not-allowed cases return `403`, если существование объекта не нужно скрывать.
- Этот ADR распространяется на будущие compatibility routes этапа 27.
- GraphQL errors этапа 28 могут иметь собственный GraphQL-формат, но должны переиспользовать те же permission and service-layer rules.
- Подробные примеры ниже являются историческим контрактным контекстом.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

В web-слое ошибки показываются через Django messages, redirects и повторный render страницы. Для REST API такой подход не подходит: API должен возвращать HTTP status codes и JSON-ответы в едином формате.

В плане этапа 12 также есть пункт:

```text
Добавить permissions.
```

На текущий момент необходимо определить:

```text
- базовый формат JSON-ошибок;
- HTTP status codes для разных типов ошибок;
- набор базовых permissions;
- поведение при доступе к чужим приватным ресурсам;
- правила преобразования ошибок service-layer в API responses;
- формат ошибок валидации serializer;
- формат бизнес-ошибок домена.
```

Без отдельного решения каждый endpoint может начать возвращать ошибки по-своему. Это усложнит тестирование, OpenAPI-документацию, frontend-интеграцию и сопровождение API.

Особенно важно зафиксировать поведение для приватных пользовательских ресурсов, например заказов. Если API будет возвращать `403 Forbidden` при обращении к чужому заказу, он может раскрыть сам факт существования чужого объекта.

## Решение

Принимаем единый API error/permission contract.

Базовый формат ошибки:

```json
{
  "code": "error_code",
  "detail": "Человекочитаемое описание ошибки.",
  "fields": null
}
```

Для ошибок валидации полей:

```json
{
  "code": "validation_error",
  "detail": "Ошибка валидации данных.",
  "fields": {
    "email": [
      "Введите корректный адрес электронной почты."
    ],
    "password": [
      "Это поле обязательно."
    ]
  }
}
```

Для ошибок, не связанных с конкретным полем:

```json
{
  "code": "cart_empty",
  "detail": "Нельзя создать заказ из пустой корзины.",
  "fields": null
}
```

Для большинства endpoints API должен возвращать ошибки в этом формате.

Допускается, что стандартные ошибки SimpleJWT на этапе MVP могут сохранять собственный формат, если их переопределение усложняет реализацию. Однако собственные endpoints проекта должны использовать единый формат.

## Базовый формат ошибки

Единый формат:

```text
code    — машинно-читаемый код ошибки;
detail  — человекочитаемое описание;
fields  — словарь ошибок по полям или null.
```

### code

`code` используется клиентами для программной обработки ошибки.

Примеры:

```text
validation_error
authentication_required
permission_denied
not_found
cart_empty
cart_has_unavailable_items
insufficient_stock
purchase_required
review_already_exists
invalid_quantity
server_error
```

### detail

`detail` содержит понятное описание ошибки для пользователя или разработчика клиента.

Пример:

```json
{
  "code": "purchase_required",
  "detail": "Оставить отзыв может только пользователь, который покупал этот товар.",
  "fields": null
}
```

### fields

`fields` используется только для ошибок serializer/form validation.

Если ошибка не связана с конкретными полями, значение должно быть:

```json
null
```

## HTTP status codes

### 400 Bad Request

Используется для ошибок входных данных и бизнес-валидации, когда запрос синтаксически корректный, но не проходит правила приложения.

Примеры:

```text
- невалидный serializer payload;
- quantity < 1;
- quantity больше MAX_CART_ITEM_QUANTITY;
- повторный отзыв на тот же товар;
- пустая корзина при создании заказа;
- корзина содержит недоступные позиции;
- неподдерживаемая сортировка;
- некорректный фильтр цены.
```

Пример:

```json
{
  "code": "cart_empty",
  "detail": "Нельзя создать заказ из пустой корзины.",
  "fields": null
}
```

### 401 Unauthorized

Используется, если пользователь не аутентифицирован, но endpoint требует JWT.

Примеры:

```text
- запрос к /api/cart/ без JWT;
- POST /api/orders/ без JWT;
- POST /api/products/<slug>/reviews/ без JWT.
```

Пример:

```json
{
  "code": "authentication_required",
  "detail": "Необходимо выполнить аутентификацию.",
  "fields": null
}
```

### 403 Forbidden

Используется, если пользователь аутентифицирован, но не имеет права выполнить действие.

Примеры:

```text
- пользователь пытается оставить отзыв без подтверждённой покупки;
- пользователь не имеет нужной роли для административного API-действия;
- пользователь пытается выполнить действие, запрещённое бизнес-правилами.
```

Пример:

```json
{
  "code": "purchase_required",
  "detail": "Оставить отзыв может только пользователь, который покупал этот товар.",
  "fields": null
}
```

### 404 Not Found

Используется, если объект не найден или его существование не должно раскрываться текущему пользователю.

Примеры:

```text
- товар не существует;
- товар скрыт, soft-deleted или неактивен;
- категория товара скрыта;
- заказ не существует;
- пользователь обращается к чужому заказу;
- приватный ресурс не принадлежит пользователю.
```

Для приватных пользовательских ресурсов применяется правило сокрытия:

```text
Чужие приватные объекты возвращают 404, а не 403.
```

Это нужно, чтобы не раскрывать факт существования чужих заказов или других приватных объектов.

Пример:

```json
{
  "code": "not_found",
  "detail": "Объект не найден.",
  "fields": null
}
```

### 409 Conflict

Используется для конфликтов состояния, когда запрос был валиден, но состояние системы изменилось или конфликтует с операцией.

Примеры:

```text
- остаток товара изменился во время создания заказа;
- конкурентная операция уже изменила ресурс;
- невозможно завершить checkout из-за race condition.
```

Для MVP допускается использовать `400 Bad Request` для части бизнес-ошибок, если service-layer ещё не различает conflict-сценарии. Однако для нехватки остатков во время атомарного checkout предпочтительный код:

```text
409 Conflict
```

Пример:

```json
{
  "code": "insufficient_stock",
  "detail": "Недостаточно товара на складе для оформления заказа.",
  "fields": null
}
```

### 500 Internal Server Error

Используется только для неожиданных ошибок сервера.

API не должен возвращать traceback пользователю.

Пример:

```json
{
  "code": "server_error",
  "detail": "Внутренняя ошибка сервера.",
  "fields": null
}
```

## Permissions

На этапе MVP принимается минимальный набор API permissions.

### IsOwner

Базовый permission для объектов, у которых есть поле владельца.

Используется для приватных объектов пользователя.

Примеры:

```text
- личные данные пользователя;
- адреса пользователя, если появятся;
- пользовательские приватные ресурсы.
```

### IsOrderOwner

Permission для заказов.

Правило:

```text
Пользователь может видеть только свои заказы.
```

Для чужого заказа API должен вернуть:

```text
404 Not Found
```

а не:

```text
403 Forbidden
```

Причина: заказ является приватным ресурсом, и API не должен раскрывать факт его существования.

### CanReviewProduct

Логическая permission/business-check для создания отзыва.

Фактическая проверка права оставить отзыв должна выполняться через:

```text
reviews.services.user_can_review_product()
```

или через сервис создания отзыва:

```text
reviews.services.create_product_review()
```

API permission может проверять только базовую аутентификацию, а бизнес-право покупки должно оставаться в service-layer.

Итоговое правило:

```text
IsAuthenticated проверяет факт входа.
reviews.services проверяет право оставить отзыв.
```

### IsAuthenticated

Используется для endpoints, доступных только авторизованным пользователям.

Примеры:

```text
- API-корзина;
- создание заказа;
- создание отзыва;
- список своих заказов;
- детали своего заказа.
```

### AllowAny

Используется для публичных read-only endpoints.

Примеры:

```text
- список товаров;
- детальная карточка товара;
- список категорий;
- опубликованные отзывы товара;
- регистрация пользователя;
- schema/docs, если они публичны в local/MVP.
```

## Правило 403 vs 404

Принимаем следующее правило:

```text
Для действий — 403.
Для чужих приватных объектов — 404.
```

### 403 Forbidden

Возвращается, когда пользователь известен, объект не является секретным сам по себе, но действие запрещено.

Примеры:

```text
- пользователь не покупал товар и пытается оставить отзыв;
- пользователь пытается выполнить admin-действие без роли;
- пользователь пытается выполнить запрещённую бизнес-операцию.
```

### 404 Not Found

Возвращается, когда сам факт существования объекта не должен быть раскрыт.

Примеры:

```text
- чужой заказ;
- чужой приватный адрес;
- чужой профиль в приватном endpoint;
- скрытый товар;
- soft-deleted товар.
```

Пример:

```text
GET /api/orders/100/
```

Если заказ `100` принадлежит другому пользователю, API возвращает:

```text
404 Not Found
```

## Service-layer errors

Service-layer не должен напрямую зависеть от DRF Response.

Доменные сервисы могут возвращать структурированный результат:

```python
{
    "ok": False,
    "code": "cart_empty",
    "error": "Нельзя создать заказ из пустой корзины.",
    "fields": None,
}
```

или выбрасывать доменные исключения.

На этапе MVP предпочтительный вариант:

```text
service-layer возвращает result dict с ok/code/error/fields.
```

Причина: такой подход уже согласуется с ранее принятыми ADR по корзине и заказам.

API-layer преобразует service result в HTTP response.

Пример маппинга:

```text
code=cart_empty                     -> 400
code=invalid_quantity               -> 400
code=cart_has_unavailable_items      -> 400
code=purchase_required              -> 403
code=review_already_exists          -> 400
code=insufficient_stock             -> 409
code=not_found                      -> 404
```

## Правило преобразования ошибок serializer

DRF serializer validation errors должны приводиться к единому формату:

```json
{
  "code": "validation_error",
  "detail": "Ошибка валидации данных.",
  "fields": {
    "rating": [
      "Убедитесь, что это значение больше либо равно 1."
    ]
  }
}
```

Не рекомендуется возвращать голый стандартный DRF response вида:

```json
{
  "rating": [
    "Убедитесь, что это значение больше либо равно 1."
  ]
}
```

Для этого в `apps/api/exceptions.py` можно реализовать custom exception handler.

## API exception handler

Для единообразия ошибок вводится общий exception handler.

Файл:

```text
apps/api/exceptions.py
```

Пример настройки:

```python
# config/settings/base.py

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.api.exceptions.api_exception_handler",
}
```

Задачи exception handler:

```text
- приводить ValidationError к формату {code, detail, fields};
- приводить NotAuthenticated к authentication_required;
- приводить PermissionDenied к permission_denied;
- приводить NotFound к not_found;
- не раскрывать внутренние ошибки сервера;
- сохранять корректный HTTP status code.
```

## Формат успешных ответов

Данный ADR не вводит обязательную обёртку для успешных ответов.

То есть успешные ответы могут оставаться ресурсными:

```json
{
  "id": 10,
  "slug": "iphone-15",
  "name": "iPhone 15"
}
```

или paginated DRF-формата:

```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": []
}
```

Единый envelope вида:

```json
{
  "data": {},
  "error": null
}
```

на этапе MVP не вводится.

Причина: это усложняет работу с DRF pagination и drf-spectacular без значимой пользы для текущего проекта.

Единый формат обязателен именно для ошибок.

## Последствия

Плюсы решения:

```text
- API получает единый формат ошибок;
- frontend/API-клиенту проще обрабатывать ошибки;
- тесты могут проверять code/detail/fields стабильно;
- Swagger/OpenAPI становится предсказуемее;
- чужие приватные объекты не раскрываются через 403;
- service-layer не зависит от DRF;
- permissions получают понятные зоны ответственности;
- бизнес-ошибки маппятся в явные HTTP status codes.
```

Минусы решения:

```text
- нужно реализовать custom exception handler;
- нужно следить, чтобы endpoints не возвращали ошибки вручную в случайном формате;
- часть стандартных DRF/SimpleJWT ошибок может потребовать адаптации;
- потребуется больше тестов на error contract;
- разработчикам нужно поддерживать список error codes.
```

## Связанные документы / файлы / настройки

```text
- docs/api.md
- docs/architecture.md
- docs/conflicts.md
- docs/decisions/0029-api-error-permissions-contract.md
- docs/decisions/0023-api-architecture-boundary.md
- docs/decisions/0025-api-cart-contract.md
- docs/decisions/0026-api-order-create-contract.md
- docs/decisions/0028-review-api-contract.md
- apps/api/exceptions.py
- apps/api/permissions.py
- apps/api/views/
- apps/api/serializers/
- apps/api/tests/test_errors.py
- apps/api/tests/test_permissions.py
- config/settings/base.py
```

## Инварианты для реализации

```text
1. API errors должны возвращаться в формате {code, detail, fields}.
2. Validation errors используют code=validation_error.
3. Ошибки без привязки к полям используют fields=null.
4. Неавторизованный доступ возвращает 401.
5. Запрещённое действие возвращает 403.
6. Чужой приватный объект возвращает 404.
7. Скрытые, удалённые и неактивные публичные объекты возвращают 404.
8. Бизнес-ошибки service-layer маппятся в согласованные HTTP status codes.
9. Service-layer не должен импортировать DRF Response.
10. API views не должны возвращать ошибки в произвольном формате.
11. Для успешных ответов единый envelope не вводится.
12. SimpleJWT endpoints могут временно сохранить стандартный формат ошибок, если не переопределены явно.
```

## Пример apps/api/exceptions.py

```python
# apps/api/exceptions.py

from rest_framework import exceptions, status
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """
    Приводит стандартные DRF-ошибки к единому формату API.
    """

    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, exceptions.ValidationError):
        response.data = {
            "code": "validation_error",
            "detail": "Ошибка валидации данных.",
            "fields": response.data,
        }
        return response

    if isinstance(exc, exceptions.NotAuthenticated):
        response.data = {
            "code": "authentication_required",
            "detail": "Необходимо выполнить аутентификацию.",
            "fields": None,
        }
        return response

    if isinstance(exc, exceptions.PermissionDenied):
        response.data = {
            "code": "permission_denied",
            "detail": "Недостаточно прав для выполнения действия.",
            "fields": None,
        }
        return response

    if isinstance(exc, exceptions.NotFound):
        response.data = {
            "code": "not_found",
            "detail": "Объект не найден.",
            "fields": None,
        }
        return response

    response.data = {
        "code": "api_error",
        "detail": response.data.get("detail", "Ошибка API."),
        "fields": None,
    }

    return response
```

## Пример helper для service result

```python
# apps/api/responses.py

from rest_framework import status
from rest_framework.response import Response


SERVICE_ERROR_STATUS_MAP = {
    "cart_empty": status.HTTP_400_BAD_REQUEST,
    "invalid_quantity": status.HTTP_400_BAD_REQUEST,
    "cart_has_unavailable_items": status.HTTP_400_BAD_REQUEST,
    "purchase_required": status.HTTP_403_FORBIDDEN,
    "review_already_exists": status.HTTP_400_BAD_REQUEST,
    "insufficient_stock": status.HTTP_409_CONFLICT,
    "not_found": status.HTTP_404_NOT_FOUND,
}


def service_error_response(result):
    """
    Преобразует ошибочный service-layer result в единый API response.
    """

    code = result.get("code", "business_rule_error")

    return Response(
        {
            "code": code,
            "detail": result.get("error", "Операция не может быть выполнена."),
            "fields": result.get("fields"),
        },
        status=SERVICE_ERROR_STATUS_MAP.get(
            code,
            status.HTTP_400_BAD_REQUEST,
        ),
    )
```

## Пример apps/api/permissions.py

```python
# apps/api/permissions.py

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Базовая проверка владения объектом.

    Ожидает, что у объекта есть поле user.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsOrderOwner(permissions.BasePermission):
    """
    Проверка владельца заказа.

    Для чужих заказов предпочтительно фильтровать queryset по request.user,
    чтобы API возвращал 404 вместо 403.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
```

## Предпочтительный способ скрывать чужие заказы

Для заказов лучше не полагаться только на object permission.

Правильнее сразу ограничить queryset:

```python
# apps/api/views/orders.py

class OrderViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
```

Тогда запрос чужого заказа:

```text
GET /api/orders/100/
```

вернёт:

```text
404 Not Found
```

даже если заказ существует в БД.

## Пример ошибки создания отзыва без покупки

```http
POST /api/products/iphone-15/reviews/
Authorization: Bearer <token>
Content-Type: application/json
```

Ответ:

```http
403 Forbidden
```

```json
{
  "code": "purchase_required",
  "detail": "Оставить отзыв может только пользователь, который покупал этот товар.",
  "fields": null
}
```

## Пример ошибки чужого заказа

```http
GET /api/orders/100/
Authorization: Bearer <token>
```

Если заказ принадлежит другому пользователю:

```http
404 Not Found
```

```json
{
  "code": "not_found",
  "detail": "Объект не найден.",
  "fields": null
}
```

## Пример ошибки валидации

```http
POST /api/users/register/
Content-Type: application/json
```

```json
{
  "username": "",
  "email": "bad-email",
  "password": "123"
}
```

Ответ:

```http
400 Bad Request
```

```json
{
  "code": "validation_error",
  "detail": "Ошибка валидации данных.",
  "fields": {
    "username": [
      "Это поле не может быть пустым."
    ],
    "email": [
      "Введите корректный адрес электронной почты."
    ],
    "password": [
      "Введённый пароль слишком короткий."
    ]
  }
}
```

## Пример тестовых ожиданий

```text
1. Serializer validation error возвращает code=validation_error.
2. Serializer validation error содержит fields.
3. Ошибка без полей содержит fields=null.
4. Запрос к /api/cart/ без JWT возвращает 401 и code=authentication_required.
5. Попытка оставить отзыв без покупки возвращает 403 и code=purchase_required.
6. Повторный отзыв возвращает 400 и code=review_already_exists.
7. Пустая корзина при checkout возвращает 400 и code=cart_empty.
8. Нехватка остатков при checkout возвращает 409 и code=insufficient_stock.
9. Чужой заказ возвращает 404 и code=not_found.
10. Скрытый товар возвращает 404 и code=not_found.
11. API views не возвращают произвольный формат ошибок.
12. Service-layer не импортирует DRF Response.
13. Успешные paginated responses остаются в стандартном DRF pagination format.
```

## Примечание по будущему развитию

В будущем можно расширить error contract дополнительными полями:

```json
{
  "code": "error_code",
  "detail": "Описание ошибки.",
  "fields": null,
  "request_id": "...",
  "docs_url": "..."
}
```

Но на этапе MVP это не требуется.

Базовое правило этапа 12:

```text
Ошибки API должны быть единообразными, предсказуемыми и безопасными.
```
