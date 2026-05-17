# ADR 0023: Архитектура REST API и граница ответственности apps/api

## Статус

Принято.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

На текущий момент API-инфраструктура уже подключена:

```text
- rest_framework;
- SimpleJWT;
- drf_spectacular;
- /api/schema/;
- /api/docs/;
- /api/token/;
- /api/token/refresh/.

Файл:

apps/api/urls.py

пока не содержит доменных маршрутов.

Доменные API-модули внутри приложений пока не созданы:

apps/catalog/api/
apps/cart/api/
apps/orders/api/
apps/reviews/api/
...
```

Ранее в docs/architecture.md был зафиксирован целевой принцип, что API-код может находиться рядом с доменным приложением, а apps/api должен собирать маршруты.

Однако перед реализацией этапа 12 принято уточнение архитектуры: если распределить API-serializers, API-views, API-permissions и API-urls по каждому доменному приложению, проект может стать сложнее сопровождать на текущем масштабе MVP.

Основной риск распределённого API-слоя:

- API-код будет размазан по нескольким приложениям;
- сложнее увидеть общий публичный контракт API;
- сложнее поддерживать единый стиль сериализаторов, permissions и ошибок;
- сложнее контролировать версионирование API;
- сложнее документировать API как единый внешний интерфейс;
- выше риск дублирования логики между API и web-слоем.

При этом важно не нарушить принципы DRY и SOLID.

API-слой не должен становиться местом бизнес-логики. Он должен быть внешним интерфейсом к уже существующим доменным правилам.

## Решение

Принимаем решение:

Вся REST API-логика размещается централизованно в приложении apps/api.

Приложение apps/api становится владельцем REST API-контракта проекта.

Внутри apps/api размещаются:

- serializers;
- views;
- viewsets;
- permissions;
- urls;
- filters;
- pagination;
- schemas;
- API-level exceptions;
- API-specific tests.

Доменные приложения остаются владельцами:

- models;
- domain services;
- бизнес-правил;
- web views;
- forms;
- templates;
- admin;
- domain tests.

REST API не должен напрямую реализовывать бизнес-логику.

API-view или API-viewset должны:

- принять HTTP-запрос;
- проверить permissions;
- провалидировать serializer;
- вызвать доменный service-layer, если операция содержит бизнес-правило;
- вернуть HTTP-ответ в согласованном формате.

Итоговый принцип:

apps/api владеет REST-контрактом.
Доменное приложение владеет бизнес-логикой.
Пересмотр предыдущего архитектурного принципа

Если в docs/architecture.md ранее было указано, что API-код должен находиться рядом с доменным приложением, это правило необходимо обновить.

Новое правило:

API-код находится централизованно в apps/api.
Доменные service-layer функции остаются внутри соответствующих приложений.

Это не нарушает разделение ответственности, если apps/api не начинает содержать бизнес-правила.

Например:

apps/api/cart/views.py       — HTTP API для корзины
apps/cart/services.py        — бизнес-логика корзины

apps/api/reviews/views.py    — HTTP API для отзывов
apps/reviews/services.py     — бизнес-логика отзывов

apps/api/orders/views.py     — HTTP API для заказов
apps/orders/services.py      — бизнес-логика заказов
Структура apps/api

Целевая структура:

apps/api/
├── __init__.py
├── urls.py
├── routers.py
├── permissions.py
├── pagination.py
├── exceptions.py
├── schema.py
├── serializers/
│   ├── __init__.py
│   ├── catalog.py
│   ├── cart.py
│   ├── orders.py
│   ├── reviews.py
│   └── users.py
├── views/
│   ├── __init__.py
│   ├── catalog.py
│   ├── cart.py
│   ├── orders.py
│   ├── reviews.py
│   └── users.py
├── filters/
│   ├── __init__.py
│   └── catalog.py
└── tests/
    ├── __init__.py
    ├── test_catalog_api.py
    ├── test_cart_api.py
    ├── test_orders_api.py
    ├── test_reviews_api.py
    └── test_schema.py

Допускается упрощённая структура на старте этапа 12, но направление должно оставаться таким:

API-контракт централизован в apps/api.
Использование DRF routers

Принимаем смешанный, но контролируемый подход:

ViewSet + router использовать для ресурсных CRUD/read-only endpoints.
APIView / GenericAPIView использовать для командных действий.
Где использовать ViewSet

ViewSet и router подходят для ресурсов:

- товары;
- категории;
- отзывы;
- заказы;

Примеры:

GET /api/products/
GET /api/products/{id}/
GET /api/categories/
GET /api/reviews/
GET /api/orders/
GET /api/orders/{id}/
Где использовать APIView / GenericAPIView

APIView или GenericAPIView подходят для команд, которые не являются обычным CRUD:

POST /api/cart/items/
PATCH /api/cart/items/{product_id}/
DELETE /api/cart/items/{product_id}/
DELETE /api/cart/
POST /api/reviews/products/{product_id}/
POST /api/checkout/

Причина:

Корзина, checkout и создание отзыва — это бизнес-команды,
а не простое редактирование модели через CRUD.
apps/api/urls.py

apps/api/urls.py является единой точкой подключения API-маршрутов.

Пример:

# apps/api/urls.py

from django.urls import include, path

from apps.api.routers import router
from apps.api.views import cart as cart_views
from apps.api.views import reviews as review_views

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),

    path(
        "cart/",
        cart_views.CartDetailAPIView.as_view(),
        name="cart-detail",
    ),
    path(
        "cart/items/",
        cart_views.CartItemAddAPIView.as_view(),
        name="cart-item-add",
    ),
    path(
        "cart/items/<int:product_id>/",
        cart_views.CartItemUpdateRemoveAPIView.as_view(),
        name="cart-item-update-remove",
    ),
    path(
        "cart/clear/",
        cart_views.CartClearAPIView.as_view(),
        name="cart-clear",
    ),
    path(
        "reviews/products/<int:product_id>/",
        review_views.ProductReviewCreateAPIView.as_view(),
        name="product-review-create",
    ),
]
apps/api/routers.py

Ресурсные endpoints подключаются через общий router:

# apps/api/routers.py

from rest_framework.routers import DefaultRouter

from apps.api.views.catalog import CategoryViewSet, ProductViewSet
from apps.api.views.orders import OrderViewSet
from apps.api.views.reviews import ReviewViewSet

router = DefaultRouter()

router.register(
    r"products",
    ProductViewSet,
    basename="product",
)

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    r"orders",
    OrderViewSet,
    basename="order",
)

router.register(
    r"reviews",
    ReviewViewSet,
    basename="review",
)
Namespaces

Основной namespace API:

api

Подключение в корневом urls.py:

path(
    "api/",
    include("apps.api.urls", namespace="api"),
)

Имена маршрутов должны быть предсказуемыми:

api:product-list
api:product-detail
api:category-list
api:category-detail
api:cart-detail
api:cart-item-add
api:cart-item-update-remove
api:cart-clear
api:order-list
api:order-detail
api:review-list
api:review-detail
api:product-review-create
Публичный API-контракт MVP

На этапе 12 публичным контрактом MVP считаются только endpoints, которые явно реализованы и покрыты тестами.

Минимальный состав API MVP:

Auth:
- POST /api/token/
- POST /api/token/refresh/

Schema:
- GET /api/schema/
- GET /api/docs/

Catalog:
- GET /api/products/
- GET /api/products/{id}/
- GET /api/categories/
- GET /api/categories/{id}/

Cart:
- GET /api/cart/
- POST /api/cart/items/
- PATCH /api/cart/items/{product_id}/
- DELETE /api/cart/items/{product_id}/
- DELETE /api/cart/clear/

Orders:
- GET /api/orders/
- GET /api/orders/{id}/

Reviews:
- GET /api/reviews/
- GET /api/reviews/{id}/
- POST /api/reviews/products/{product_id}/

Если часть endpoints не реализуется на этапе 12, она не считается публичным контрактом и не должна быть указана как готовая в документации.

Правила DRY и SOLID

apps/api не должен дублировать бизнес-логику.

Запрещено:

- пересчитывать корзину внутри API-view;
- создавать заказ напрямую в API-view без checkout/order service;
- проверять право на отзыв вручную в API-view, если есть reviews.services;
- дублировать правила статусов заказов;
- дублировать правила количества товара в корзине;
- дублировать нормализацию session-cart;
- смешивать serializer validation и бизнес-правила домена.

Допустимо:

- проверять формат входных данных через serializer;
- проверять permissions на уровне API;
- преобразовывать domain result в HTTP response;
- использовать разные serializers для read/write;
- использовать разные serializers для list/detail;
- использовать service-layer для операций с бизнес-смыслом.

Пример правильной границы:

# apps/api/views/cart.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart import services as cart_services
from apps.catalog.models import Product
from apps.api.serializers.cart import CartItemAddSerializer


class CartItemAddAPIView(APIView):
    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(
            id=serializer.validated_data["product_id"],
        )

        result = cart_services.add_to_cart(
            request=request,
            product=product,
            quantity=serializer.validated_data["quantity"],
        )

        if not result["ok"]:
            return Response(
                {"detail": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            result["snapshot"],
            status=status.HTTP_200_OK,
        )
Последствия

Плюсы решения:

- REST API-контракт проекта находится в одном месте;
- проще видеть весь внешний API;
- проще поддерживать единый стиль serializers, permissions и errors;
- проще поддерживать drf-spectacular schema;
- проще тестировать API как внешний слой;
- доменные приложения не захламляются API-кодом;
- бизнес-логика остаётся в service-layer;
- соблюдается DRY за счёт переиспользования доменных сервисов;
- соблюдается SOLID за счёт отделения HTTP API от доменных правил.

Минусы решения:

- apps/api может стать крупным приложением;
- нужна дисциплина в структуре подпакетов serializers/views/tests;
- появляется риск случайно перенести бизнес-логику в apps/api;
- при большом росте проекта может потребоваться пересмотр в сторону доменных api-модулей;
- docs/architecture.md нужно обновить под новое решение.
Связанные документы / файлы / настройки
- docs/architecture.md
- docs/conflicts.md
- docs/decisions/0023-api-architecture-boundary.md
- config/urls.py
- config/settings/base.py
- apps/api/urls.py
- apps/api/routers.py
- apps/api/serializers/
- apps/api/views/
- apps/api/permissions.py
- apps/api/pagination.py
- apps/api/tests/
- apps/catalog/models.py
- apps/cart/services.py
- apps/orders/services.py
- apps/reviews/services.py
Инварианты для реализации
1. REST API-код находится в apps/api.
2. serializers, API views, API permissions и API urls размещаются внутри apps/api.
3. Доменные приложения не содержат собственные api/views.py и api/serializers.py на этапе MVP.
4. apps/api не содержит бизнес-логику домена.
5. Бизнес-операции вызывают доменные service-layer функции.
6. ViewSet + router используются для ресурсных endpoints.
7. APIView / GenericAPIView используются для командных endpoints.
8. apps/api/urls.py является единой точкой подключения API.
9. API namespace — api.
10. drf-spectacular schema должна описывать только реально поддержанные endpoints.
11. Web views и API views не должны наследоваться друг от друга.
12. API не должен ломать уже принятые ADR по корзине, заказам и отзывам.
Пример структуры импортов

Правильно:

from apps.cart import services as cart_services
from apps.reviews import services as review_services
from apps.catalog.models import Product
from apps.api.serializers.cart import CartItemAddSerializer

Нежелательно:

from apps.catalog.views import ProductDetailView
from apps.cart.views import CartAddView

API не должен переиспользовать web views.

Web и API — разные HTTP-интерфейсы, но они могут использовать общие доменные сервисы.

Пример тестовых ожиданий
1. API catalog endpoints находятся в apps/api/views/catalog.py.
2. API cart endpoints находятся в apps/api/views/cart.py.
3. API serializers находятся в apps/api/serializers/.
4. apps/catalog не содержит API-specific views на этапе MVP.
5. apps/cart/services.py используется API endpoints корзины.
6. API cart add не дублирует quantity-политику.
7. API review create использует reviews.services.create_product_review().
8. apps/api/urls.py подключает все API routes.
9. /api/schema/ содержит реализованные endpoints.
10. Web views не используются внутри API views.
11. API views не используются внутри web views.
12. Бизнес-правила покрываются service tests, HTTP-контракт покрывается API tests.
Примечание по будущему масштабированию

Если проект существенно вырастет, допускается пересмотр этого решения.

Возможный будущий вариант:

apps/catalog/api/
apps/cart/api/
apps/orders/api/
apps/reviews/api/

Но переход к распределённому API-слою должен быть оформлен отдельным ADR.

До такого решения действует правило:

REST API централизован в apps/api.
Бизнес-логика остаётся в доменных service-layer.
