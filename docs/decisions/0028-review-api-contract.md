# ADR 0028: Контракт Review API и связь с web-сценарием отзывов

## Статус

Принято.

## Актуальная сжатая версия

- Review API должен переиспользовать `reviews.services` и не обходить правила подтверждённой покупки.
- Публичный список отзывов показывает опубликованные отзывы.
- Новый отзыв создаётся в статусе `pending`.
- Действующий контракт связан с product slug.
- После появления конфликта `C036` slug route сохраняется, а необходимость id compatibility route решается на этапе 27.
- Ошибки Review API должны использовать единый формат ADR 0029.
- Подробные примеры ниже являются историческим контрактным контекстом.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

На этапе 11 уже реализован web-сценарий создания отзыва:

```text
POST /reviews/products/<slug>/add/

Право оставить отзыв проверяется через сервис:

reviews.services.user_can_review_product()

Создание отзыва выполняется через review service.

Новый отзыв создаётся в статусе:

pending

Публично на странице товара отображаются только опубликованные отзывы.

В docs/api.md ранее был указан предварительный API-план:

POST /api/products/<id>/reviews/
```

Однако Product API уже использует slug как публичный lookup товара. Если Review API начнёт использовать id, появится расхождение между web-контрактом, Product API и Review API.

Конфликт C029 связан с тем, как должен выглядеть публичный контракт API отзывов и как он должен быть связан с уже реализованной web-логикой.

## Решение

Принимаем решение:

Review API использует slug товара как публичный lookup.

Канонические endpoints этапа 12:

GET  /api/products/<slug>/reviews/    — список опубликованных отзывов товара
POST /api/products/<slug>/reviews/    — создать отзыв на товар

Endpoint:

POST /api/products/<id>/reviews/

не используется как публичный контракт MVP.

Причина:

Product API и web-каталог уже используют slug как публичный идентификатор товара.
Review API должен быть согласован с этим правилом.
Связь с web-сценарием

Web-сценарий:

POST /reviews/products/<slug>/add/

и API-сценарий:

POST /api/products/<slug>/reviews/

должны использовать один и тот же доменный service-layer.

API не должен самостоятельно реализовывать правила:

- проверка подтверждённой покупки;
- проверка уникальности user + product;
- выставление is_verified_purchase;
- выбор начального status;
- запрет повторного отзыва;
- проверка права пользователя оставить отзыв.

Эти правила принадлежат:

apps/reviews/services.py

Основной сервис:

reviews.services.create_product_review()

или эквивалентная доменная функция, если фактическое имя отличается.

Авторизация

Создание отзыва через API требует JWT-аутентификацию.

POST /api/products/<slug>/reviews/ требует JWT.

Если пользователь не авторизован:

401 Unauthorized

Получение опубликованных отзывов товара доступно публично:

GET /api/products/<slug>/reviews/ доступен без JWT.

Причина:

Опубликованные отзывы являются частью публичного каталога.
Создание отзыва является пользовательским действием и требует авторизации.
GET /api/products/<slug>/reviews/

Endpoint возвращает только опубликованные отзывы товара.

GET /api/products/<slug>/reviews/

Правило публичной видимости:

В публичном списке отзывов отображаются только отзывы со статусом published.

Отзывы в статусах ниже не возвращаются в публичном списке:

pending
rejected
hidden
draft
deleted

Если товар не найден, неактивен, soft-deleted или находится в неактивной категории:

404 Not Found

API не должен раскрывать существование скрытых товаров.

Response списка отзывов

Список отзывов должен быть paginated.

Пример:

{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 101,
      "rating": 5,
      "title": "Отличный товар",
      "text": "Покупкой доволен.",
      "status": "published",
      "is_verified_purchase": true,
      "author": {
        "id": 42,
        "username": "ivan"
      },
      "created_at": "2026-05-18T10:00:00Z",
      "updated_at": "2026-05-18T10:00:00Z"
    }
  ]
}
POST /api/products/<slug>/reviews/

Endpoint создаёт отзыв на товар.

POST /api/products/<slug>/reviews/
Authorization: Bearer <token>
Content-Type: application/json
Payload создания отзыва

Минимальный payload:

{
  "rating": 5,
  "title": "Отличный товар",
  "text": "Покупкой доволен."
}

Поля:

rating  — обязательное;
title   — обязательное или необязательное согласно текущей модели/форме;
text    — обязательное.

Для этапа 12 принимаем правило:

rating и text обязательны.
title допускается как необязательное поле, если модель позволяет blank=True.

Если в текущей модели Review.title обязательный, API serializer должен сделать title обязательным.

Начальный статус нового отзыва

Новый отзыв, созданный через API, получает тот же начальный статус, что и web-сценарий:

pending

API не публикует отзыв сразу.

Публичное отображение отзыва возможно только после модерации и перевода в статус:

published

Это должно быть одинаково для web и API.

Response успешного создания

После успешного создания API возвращает:

201 Created

Response содержит созданный отзыв, включая его текущий статус:

{
  "id": 101,
  "product": {
    "id": 10,
    "slug": "iphone-15",
    "name": "iPhone 15"
  },
  "rating": 5,
  "title": "Отличный товар",
  "text": "Покупкой доволен.",
  "status": "pending",
  "is_verified_purchase": true,
  "created_at": "2026-05-18T10:00:00Z",
  "message": "Отзыв отправлен и будет опубликован после проверки."
}

Важно:

Автор получает свой pending-отзыв в response после создания.

Но этот отзыв не появляется в публичном GET /api/products/<slug>/reviews/, пока не будет опубликован.

Нужно ли отдавать pending-отзыв автору

В рамках публичного списка отзывов товара:

pending-отзывы не отображаются.

В рамках response после создания:

pending-отзыв возвращается автору.

Это нормальное поведение: пользователь должен понимать, что отзыв принят системой и ожидает модерации.

Отдельный endpoint для списка собственных отзывов пользователя на этапе MVP можно не реализовывать.

В будущем допустим endpoint:

GET /api/users/me/reviews/

Он сможет показывать пользователю его отзывы, включая pending.

Но это не входит в минимальный контракт C029.

Ошибки
Пользователь не авторизован
401 Unauthorized

Пример:

{
  "detail": "Authentication credentials were not provided."
}
Товар не найден или скрыт
404 Not Found

Пример:

{
  "detail": "Товар не найден."
}
Пользователь не покупал товар

Если пользователь не имеет подтверждённой покупки товара согласно ADR 0021:

403 Forbidden

Пример:

{
  "detail": "Оставить отзыв может только пользователь, который покупал этот товар.",
  "code": "purchase_required"
}
Повторный отзыв

Если пользователь уже оставил отзыв на этот товар:

400 Bad Request

или:

409 Conflict

Для MVP принимаем:

400 Bad Request

Пример:

{
  "detail": "Вы уже оставили отзыв на этот товар.",
  "code": "review_already_exists"
}

Причина: проще реализовать и документировать в DRF serializer/service contract.

Если в будущем API будет строже разделять validation и state conflict, можно перейти на 409 Conflict отдельным ADR.

Невалидный rating

Если rating вне допустимого диапазона:

400 Bad Request

Пример:

{
  "rating": [
    "Оценка должна быть от 1 до 5."
  ]
}
Невалидный text/title

Если обязательный текст отсутствует или не проходит ограничения длины:

400 Bad Request

Пример:

{
  "text": [
    "Это поле обязательно."
  ]
}
Связь с Product detail API

Product detail API не должен включать полный список отзывов.

Product detail возвращает только агрегаты:

average_rating
reviews_count

Полный список отзывов получается отдельно:

GET /api/products/<slug>/reviews/

Это согласуется с ADR 0025.

Причина:

Отзывы являются отдельной коллекцией с собственной пагинацией, модерацией и правами доступа.
Граница ответственности

API-код находится в:

apps/api

Например:

apps/api/views/reviews.py
apps/api/serializers/reviews.py

Бизнес-логика находится в:

apps/reviews/services.py

API view отвечает за:

- JWT-аутентификацию;
- поиск публичного товара по slug;
- serializer validation;
- вызов reviews.services;
- преобразование результата service-layer в HTTP response.

API view не должен:

- напрямую создавать Review.objects.create();
- самостоятельно выставлять is_verified_purchase;
- самостоятельно определять право пользователя оставить отзыв;
- самостоятельно проверять статусы заказов;
- дублировать правило user + product unique;
- публиковать отзыв в обход модерации.
Последствия

Плюсы решения:

- Review API согласован с web URL и Product API через slug;
- web и API используют единый reviews service-layer;
- правила покупки и уникальности не дублируются;
- новый отзыв проходит ту же pending-модерацию, что web-отзыв;
- публичный список отзывов остаётся безопасным и показывает только published;
- Product detail API не раздувается вложенными отзывами;
- endpoint легко описывается в Swagger/OpenAPI;
- будущий endpoint собственных отзывов пользователя можно добавить без ломки контракта.

Минусы решения:

- API-клиент должен использовать slug товара, а не id;
- pending-отзыв не виден в публичном списке после создания;
- для просмотра всех собственных pending-отзывов в будущем нужен отдельный endpoint;
- POST и GET на одном URL имеют разную модель доступа;
- если slug товара изменится, старый URL создания отзыва перестанет работать.
Связанные документы / файлы / настройки
- docs/api.md
- docs/architecture.md
- docs/decisions/0021-review-eligible-order-status.md
- docs/decisions/0022-review-web-create-contract.md
- docs/decisions/0023-api-architecture-boundary.md
- docs/decisions/0024-product-api-contract.md
- docs/conflicts.md
- docs/decisions/0028-review-api-contract.md
- apps/api/views/reviews.py
- apps/api/serializers/reviews.py
- apps/api/urls.py
- apps/api/tests/test_reviews_api.py
- apps/reviews/models.py
- apps/reviews/services.py
- apps/catalog/models.py
- apps/orders/models.py
Инварианты для реализации
1. Review API для товара использует product slug.
2. POST /api/products/<slug>/reviews/ требует JWT.
3. GET /api/products/<slug>/reviews/ доступен публично.
4. GET возвращает только published-отзывы.
5. POST создаёт отзыв через reviews.services.create_product_review().
6. API не создаёт Review напрямую.
7. Новый API-отзыв создаётся в статусе pending.
8. Response после создания возвращает pending-отзыв автору.
9. Pending-отзыв не появляется в публичном списке отзывов.
10. Право оставить отзыв проверяется через reviews.services.user_can_review_product().
11. is_verified_purchase выставляется в service-layer.
12. Повторный отзыв одного пользователя на один товар запрещён.
13. Product detail API содержит rating aggregates, но не полный список отзывов.
14. POST /api/products/<id>/reviews/ не является публичным endpoint MVP.
Пример API serializer
# apps/api/serializers/reviews.py

from rest_framework import serializers


class ProductReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
    )
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    text = serializers.CharField()


class ReviewAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class ProductReviewReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rating = serializers.IntegerField()
    title = serializers.CharField()
    text = serializers.CharField()
    status = serializers.CharField()
    is_verified_purchase = serializers.BooleanField()
    author = ReviewAuthorSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

Фактическая реализация может использовать ModelSerializer, но публичный контракт должен соответствовать этому ADR.

Пример API view
# apps/api/views/reviews.py

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.reviews import ProductReviewCreateSerializer
from apps.catalog.models import Product
from apps.reviews import services as review_services
from apps.reviews.models import Review


class ProductReviewListCreateAPIView(APIView):
    """
    GET: публичный список опубликованных отзывов товара.
    POST: создание pending-отзыва авторизованным пользователем.
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_product(self, slug):
        return get_object_or_404(
            Product.objects.filter(
                slug=slug,
                is_active=True,
                is_deleted=False,
                category__is_active=True,
                category__is_deleted=False,
            )
        )

    def get(self, request, slug):
        product = self.get_product(slug)

        reviews = (
            Review.objects
            .filter(
                product=product,
                status=Review.Status.PUBLISHED,
            )
            .select_related("user")
            .order_by("-created_at")
        )

        # Реальная реализация должна использовать DRF pagination.
        data = [
            {
                "id": review.id,
                "rating": review.rating,
                "title": review.title,
                "text": review.text,
                "status": review.status,
                "is_verified_purchase": review.is_verified_purchase,
                "author": {
                    "id": review.user_id,
                    "username": review.user.username,
                },
                "created_at": review.created_at,
                "updated_at": review.updated_at,
            }
            for review in reviews
        ]

        return Response(
            {
                "count": len(data),
                "next": None,
                "previous": None,
                "results": data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, slug):
        product = self.get_product(slug)

        serializer = ProductReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = review_services.create_product_review(
            user=request.user,
            product=product,
            rating=serializer.validated_data["rating"],
            title=serializer.validated_data.get("title", ""),
            text=serializer.validated_data["text"],
        )

        if not result["ok"]:
            return Response(
                {
                    "detail": result["error"],
                    "code": result.get("code"),
                },
                status=status.HTTP_403_FORBIDDEN
                if result.get("code") == "purchase_required"
                else status.HTTP_400_BAD_REQUEST,
            )

        review = result["review"]

        return Response(
            {
                "id": review.id,
                "product": {
                    "id": product.id,
                    "slug": product.slug,
                    "name": product.name,
                },
                "rating": review.rating,
                "title": review.title,
                "text": review.text,
                "status": review.status,
                "is_verified_purchase": review.is_verified_purchase,
                "created_at": review.created_at,
                "message": "Отзыв отправлен и будет опубликован после проверки.",
            },
            status=status.HTTP_201_CREATED,
        )
Пример URL
# apps/api/urls.py

from django.urls import path

from apps.api.views import reviews as review_views

app_name = "api"

urlpatterns = [
    path(
        "products/<slug:slug>/reviews/",
        review_views.ProductReviewListCreateAPIView.as_view(),
        name="product-review-list-create",
    ),
]
Пример успешного создания

Запрос:

POST /api/products/iphone-15/reviews/
Authorization: Bearer <token>
Content-Type: application/json
{
  "rating": 5,
  "title": "Отличный товар",
  "text": "Покупкой доволен."
}

Ответ:

201 Created
{
  "id": 101,
  "product": {
    "id": 10,
    "slug": "iphone-15",
    "name": "iPhone 15"
  },
  "rating": 5,
  "title": "Отличный товар",
  "text": "Покупкой доволен.",
  "status": "pending",
  "is_verified_purchase": true,
  "created_at": "2026-05-18T10:00:00Z",
  "message": "Отзыв отправлен и будет опубликован после проверки."
}
Пример тестовых ожиданий
1. GET /api/products/<slug>/reviews/ возвращает только published-отзывы.
2. GET /api/products/<slug>/reviews/ не возвращает pending-отзывы.
3. GET /api/products/<slug>/reviews/ не возвращает rejected/hidden-отзывы.
4. GET /api/products/<slug>/reviews/ доступен без JWT.
5. POST /api/products/<slug>/reviews/ без JWT возвращает 401.
6. POST /api/products/<slug>/reviews/ создаёт отзыв при подтверждённой покупке.
7. POST /api/products/<slug>/reviews/ использует reviews.services.create_product_review().
8. Созданный через API отзыв получает status=pending.
9. Response после создания содержит status=pending.
10. Response после создания содержит is_verified_purchase=True.
11. Пользователь без покупки получает 403 с code=purchase_required.
12. Повторный отзыв возвращает 400 с code=review_already_exists.
13. Невалидный rating возвращает 400.
14. Скрытый или удалённый товар возвращает 404.
15. POST /api/products/<id>/reviews/ не является публичным endpoint.
16. Product detail API не содержит полный список отзывов.
Примечание по будущему развитию

В будущем можно добавить отдельные endpoints:

GET /api/users/me/reviews/
GET /api/reviews/<id>/
PATCH /api/reviews/<id>/
DELETE /api/reviews/<id>/
POST /api/reviews/<id>/moderate/

Но они должны быть оформлены отдельным решением, потому что требуют правил:

- может ли пользователь редактировать pending-отзыв;
- может ли пользователь удалить опубликованный отзыв;
- кто модерирует отзывы;
- какие статусы доступны через API;
- какие отзывы видит автор в личном кабинете.

На этапе MVP действует правило:

Review API поддерживает публичный список published-отзывов товара
и создание pending-отзыва авторизованным покупателем товара.
