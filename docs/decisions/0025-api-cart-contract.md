# ADR 0025: Контракт API-корзины и связь с web/session-корзиной

## Статус

Принято.

## Актуальная сжатая версия

- API-корзина работает с DB-cart авторизованного JWT-пользователя.
- Гостевая session-cart остаётся web-сценарием и не становится основным API-контрактом.
- API должен переиспользовать cart service layer и возвращать нормализованный cart snapshot.
- После появления конфликта `C036` текущие granular routes сохраняются, но этап 27 должен добавить совместимый контракт `GET/POST/PATCH/DELETE /api/cart/`.
- Ошибки API-корзины должны использовать единый формат ADR 0029.
- Подробные примеры ниже являются историческим контрактным контекстом.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

В web-интерфейсе корзина уже проектируется как гибридная:

```text
- гость использует session-cart;
- авторизованный пользователь использует DB-cart;
- после входа session-cart объединяется с DB-cart;
- все операции корзины проходят через apps/cart/services.py.
```

Для web-интерфейса такой подход оправдан, потому что браузерный пользователь может работать с корзиной до авторизации, а состояние гостевой корзины хранится в session.

Однако REST API уже использует JWT-аутентификацию:

/api/token/
/api/token/refresh/

Если API-корзина начнёт поддерживать session-cart для анонимных клиентов, API станет зависеть от cookie/session-состояния браузера. Это плохо сочетается с JWT-подходом, усложняет мобильных/API-клиентов и создаёт два разных поведения корзины в одном API.

Конфликт C026 связан с тем, должна ли API-корзина повторять гостевой web-сценарий или быть отдельным авторизованным контрактом поверх DB-cart.

## Решение

Принимаем решение:

API-корзина доступна только авторизованным пользователям.

Все endpoints API-корзины требуют JWT-аутентификацию.

API-корзина:

- не поддерживает анонимную session-cart;
- не использует Django session как storage;
- не зависит от cookies;
- работает только с DB-cart авторизованного пользователя;
- использует доменный service-layer корзины;
- возвращает snapshot корзины после операций.

Если клиент обращается к API-корзине без JWT, API должен вернуть:

401 Unauthorized

Web-корзина и API-корзина используют общий доменный service-layer, но имеют разный внешний контракт:

web:
- гость: session-cart;
- пользователь: DB-cart;
- HTTP forms + redirects.

api:
- только авторизованный пользователь;
- только DB-cart;
- JSON request/response;
- JWT auth;
- без redirect.
Причина решения

API-клиент должен работать предсказуемо и stateless относительно браузерной session.

JWT API не должен требовать:

- cookie sessionid;
- csrf token для session-cart;
- браузерное состояние;
- merge guest cart при login.

Гостевой сценарий корзины остаётся частью web-интерфейса.

Для API MVP корзина является персональным ресурсом авторизованного пользователя.

Канонические endpoints API-корзины

Принимается явный набор endpoints вместо одного POST /api/cart/.

GET    /api/cart/                         — получить snapshot корзины
POST   /api/cart/items/                   — добавить товар в корзину
PATCH  /api/cart/items/<int:product_id>/  — изменить количество товара
DELETE /api/cart/items/<int:product_id>/  — удалить товар из корзины
DELETE /api/cart/clear/                   — очистить корзину

Endpoint:

POST /api/cart/

не используется как универсальный action-endpoint.

Причина:

Явные endpoints проще документировать, тестировать и поддерживать.
Идентификатор товара

Для операций корзины используется:

product_id

Это согласуется с web-контрактом корзины из ADR 0013.

Причина:

Корзина хранит позиции по внутреннему Product.id, а не по Product.slug.

Slug остаётся публичным идентификатором товара в Product API, но корзина использует product_id как стабильную ссылку на товарную позицию.

Формат payload
Добавление товара
POST /api/cart/items/
Authorization: Bearer <token>
Content-Type: application/json
{
  "product_id": 10,
  "quantity": 2
}

Правило:

add увеличивает количество существующей позиции.

Это соответствует ADR 0016.

Изменение количества
PATCH /api/cart/items/10/
Authorization: Bearer <token>
Content-Type: application/json
{
  "quantity": 5
}

Правило:

update заменяет количество позиции.

Это соответствует ADR 0016.

Удаление позиции
DELETE /api/cart/items/10/
Authorization: Bearer <token>

Тело запроса не требуется.

Очистка корзины
DELETE /api/cart/clear/
Authorization: Bearer <token>

Тело запроса не требуется.

Формат ответа snapshot корзины

Все успешные операции корзины возвращают актуальный snapshot корзины.

Пример:

{
  "items": [
    {
      "product": {
        "id": 10,
        "slug": "iphone-15",
        "name": "iPhone 15",
        "price": "89990.00",
        "url": "/api/products/iphone-15/",
        "web_url": "/products/iphone-15/"
      },
      "quantity": 2,
      "unit_price": "89990.00",
      "total_price": "179980.00",
      "is_available": true,
      "availability_message": null
    }
  ],
  "items_count": 1,
  "total_quantity": 2,
  "total_price": "179980.00",
  "has_unavailable_items": false,
  "can_checkout": true,
  "warnings": [],
  "is_empty": false
}

Корзина API должна использовать актуальные данные из Product.

Session/cart payload не является источником цены, активности или остатка.

HTTP-статусы
Успешное получение корзины
GET /api/cart/ -> 200 OK
Успешное добавление товара
POST /api/cart/items/ -> 200 OK

или допустимо:

201 Created

Для MVP принимается:

200 OK

Причина: операция может как создать новую позицию, так и увеличить существующую.

Успешное изменение количества
PATCH /api/cart/items/<product_id>/ -> 200 OK
Успешное удаление позиции
DELETE /api/cart/items/<product_id>/ -> 200 OK

Возвращается обновлённый snapshot корзины.

Успешная очистка корзины
DELETE /api/cart/clear/ -> 200 OK

Возвращается пустой snapshot корзины.

Неавторизованный запрос
401 Unauthorized
Нет прав доступа

На этапе MVP корзина пользователя доступна только самому пользователю.

Если появится сценарий доступа к чужой корзине, он должен вернуть:

403 Forbidden

Но в текущем контракте endpoints не принимают user_id, поэтому прямой доступ к чужой корзине отсутствует.

Товар не найден или недоступен

Если product_id не найден, товар неактивен, soft-deleted или находится в скрытой категории:

404 Not Found

API не должен раскрывать существование скрытых товаров.

Ошибка количества

Если quantity некорректно:

400 Bad Request

Примеры:

{
  "detail": "Количество товара должно быть больше нуля."
}
{
  "detail": "Нельзя добавить больше товара, чем доступно."
}
{
  "detail": "Количество превышает системный лимит позиции."
}
Правила количества

API-корзина использует правила ADR 0016:

- quantity должно быть целым числом больше нуля;
- add складывает количество;
- update заменяет количество;
- пользовательское превышение остатка возвращает ошибку;
- silent-обрезание add/update не допускается;
- MAX_CART_ITEM_QUANTITY = 99;
- при ошибке корзина не изменяется.
Недоступные и битые позиции

API-корзина использует правила ADR 0017:

- удалённые товары удаляются из корзины при нормализации;
- soft-deleted товары удаляются из корзины при нормализации;
- неактивные товары удаляются из корзины при нормализации;
- товары из скрытых категорий удаляются из корзины при нормализации;
- товары с stock_quantity = 0 остаются в корзине, но помечаются как недоступные;
- quantity больше текущего остатка не обрезается автоматически при чтении;
- snapshot содержит warnings;
- can_checkout=false, если есть недоступные позиции.

Для API это означает:

GET /api/cart/

может вернуть snapshot с предупреждениями.

Пример:

{
  "items": [
    {
      "product": {
        "id": 10,
        "slug": "iphone-15",
        "name": "iPhone 15"
      },
      "quantity": 2,
      "unit_price": "89990.00",
      "total_price": "179980.00",
      "is_available": false,
      "availability_message": "Количество превышает доступный остаток."
    }
  ],
  "has_unavailable_items": true,
  "can_checkout": false,
  "warnings": [
    "Некоторые товары в корзине сейчас недоступны для оформления."
  ],
  "is_empty": false
}
Связь с web/session-корзиной

API не работает с гостевой session-cart.

Если пользователь сначала добавил товары в web session-cart как гость, а затем авторизовался через web login-flow, merge выполняется в web-сценарии согласно ADR 0015.

После этого API сможет работать уже с DB-cart пользователя.

Но API login/token endpoint сам по себе не выполняет merge session-cart.

Правило:

/api/token/ не объединяет session-cart с DB-cart.

Причина:

JWT endpoint не должен зависеть от браузерной session-cart.

Если в будущем потребуется API guest-cart, это должно быть отдельным ADR.

Граница ответственности

API views находятся в apps/api.

Бизнес-логика корзины остаётся в apps/cart/services.py.

API views отвечают за:

- JWT-аутентификацию;
- permissions;
- serializer validation;
- получение Product;
- вызов cart service;
- преобразование результата сервиса в JSON response.

API views не должны:

- напрямую менять Cart/CartItem;
- напрямую читать или писать request.session["cart"];
- дублировать quantity-политику;
- дублировать нормализацию корзины;
- пересчитывать totals самостоятельно.
Последствия

Плюсы решения:

- API остаётся JWT-first и не зависит от cookies;
- API-клиенты получают предсказуемый контракт;
- нет смешения session-cart и DB-cart в API;
- проще тестировать API-корзину;
- проще документировать OpenAPI schema;
- web guest-cart остаётся отдельным UX-сценарием;
- бизнес-логика переиспользуется через apps/cart/services.py;
- API не дублирует web forms и redirects.

Минусы решения:

- анонимный API-клиент не может использовать корзину;
- API не повторяет полностью web-сценарий гостевой корзины;
- мобильному клиенту нужно сначала авторизоваться;
- если нужен guest checkout через API, потребуется отдельное архитектурное решение;
- /api/token/ не переносит session-cart автоматически.
Связанные документы / файлы / настройки
- docs/api.md
- docs/architecture.md
- docs/decisions/0002-session-cart.md
- docs/decisions/0013-cart-web-routes.md
- docs/decisions/0014-cart-service-layer.md
- docs/decisions/0015-cart-merge-timing.md
- docs/decisions/0016-cart-quantity-policy.md
- docs/decisions/0017-session-cart-invalid-products.md
- docs/decisions/0023-api-architecture-boundary.md
- docs/conflicts.md
- docs/decisions/0025-api-cart-contract.md
- apps/api/views/cart.py
- apps/api/serializers/cart.py
- apps/api/permissions.py
- apps/api/urls.py
- apps/api/tests/test_cart_api.py
- apps/cart/services.py
- apps/cart/models.py
Инварианты для реализации
1. API-корзина требует JWT-аутентификацию.
2. Анонимный доступ к API-корзине запрещён.
3. API-корзина не использует session-cart.
4. API-корзина работает только с DB-cart пользователя.
5. API-корзина использует apps/cart/services.py.
6. API views не содержат бизнес-логику корзины.
7. Product передаётся через product_id.
8. POST /api/cart/items/ добавляет товар и увеличивает количество существующей позиции.
9. PATCH /api/cart/items/<product_id>/ заменяет количество позиции.
10. DELETE /api/cart/items/<product_id>/ удаляет позицию.
11. DELETE /api/cart/clear/ очищает корзину.
12. Все успешные операции возвращают актуальный snapshot корзины.
13. Некорректное quantity возвращает 400.
14. Недоступный product_id возвращает 404.
15. /api/token/ не выполняет merge session-cart.
16. Guest-cart API не реализуется на этапе MVP.
Пример структуры API views
# apps/api/views/cart.py

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.cart import (
    CartItemAddSerializer,
    CartItemUpdateSerializer,
)
from apps.cart import services as cart_services
from apps.catalog.models import Product


class CartDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        snapshot = cart_services.get_cart_snapshot(request)
        return Response(snapshot, status=status.HTTP_200_OK)


class CartItemAddAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            Product.objects.filter(
                is_active=True,
                is_deleted=False,
                category__is_active=True,
                category__is_deleted=False,
            ),
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


class CartItemUpdateRemoveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, product_id):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(
            Product.objects.filter(
                is_active=True,
                is_deleted=False,
                category__is_active=True,
                category__is_deleted=False,
            ),
            id=product_id,
        )

        result = cart_services.update_cart_item(
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

    def delete(self, request, product_id):
        product = get_object_or_404(
            Product.objects.filter(
                is_active=True,
                is_deleted=False,
                category__is_active=True,
                category__is_deleted=False,
            ),
            id=product_id,
        )

        result = cart_services.remove_from_cart(
            request=request,
            product=product,
        )

        return Response(
            result["snapshot"],
            status=status.HTTP_200_OK,
        )


class CartClearAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        result = cart_services.clear_cart(request)
        return Response(
            result["snapshot"],
            status=status.HTTP_200_OK,
        )
Пример serializers
# apps/api/serializers/cart.py

from rest_framework import serializers


class CartItemAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
Пример URL
# apps/api/urls.py

from django.urls import path

from apps.api.views import cart as cart_views

app_name = "api"

urlpatterns = [
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
]
Пример тестовых ожиданий
1. GET /api/cart/ без JWT возвращает 401.
2. POST /api/cart/items/ без JWT возвращает 401.
3. Авторизованный GET /api/cart/ возвращает snapshot DB-cart.
4. Авторизованный POST /api/cart/items/ добавляет товар в DB-cart.
5. Повторный POST /api/cart/items/ увеличивает количество позиции.
6. PATCH /api/cart/items/<product_id>/ заменяет количество.
7. DELETE /api/cart/items/<product_id>/ удаляет позицию.
8. DELETE /api/cart/clear/ очищает корзину.
9. API-корзина не пишет в request.session["cart"].
10. Некорректное quantity возвращает 400.
11. Превышение stock_quantity возвращает 400 и не меняет корзину.
12. Неактивный товар возвращает 404.
13. Soft-deleted товар возвращает 404.
14. Товар из неактивной категории возвращает 404.
15. Все успешные операции возвращают snapshot.
16. /api/token/ не выполняет merge session-cart.
Примечание по будущему развитию

Если в будущем потребуется анонимная API-корзина, нужно будет принять отдельное ADR.

Возможные варианты будущего развития:

- guest cart token;
- server-side anonymous cart id;
- client-side cart в mobile/frontend;
- отдельный guest checkout API;
- merge guest API cart после JWT login.

На этапе MVP действует правило:

REST API корзины доступен только авторизованным пользователям и работает только с DB-cart.
