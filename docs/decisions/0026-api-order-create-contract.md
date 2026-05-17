# ADR 0026: Контракт создания заказа через API

## Статус

Принято.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

В web-интерфейсе checkout уже реализован:

```text
- заказ создаётся из текущей корзины;
- orders.services.create_order_from_cart() принимает CartSnapshot;
- создание заказа выполняется атомарно;
- товары блокируются через select_for_update();
- создаётся mock-платёж;
- после успешного checkout корзина очищается.
```

В docs/api.md предварительно указан endpoint:

POST /api/orders/

Однако перед реализацией API необходимо определить, как именно создаётся заказ:

- из текущей корзины пользователя;
- или из списка позиций, переданного в request payload;
- какие контактные и delivery-поля обязательны;
- очищается ли корзина после успешного заказа;
- используется ли тот же service-layer, что и web checkout;
- создаётся ли mock-payment так же, как в web-сценарии.

Конфликт C027 связан с тем, что API может потенциально позволить клиенту передавать позиции заказа напрямую. Это опасно, потому что такой подход может обойти правила корзины, нормализацию, проверку остатков и уже принятые ADR по cart service-layer.

## Решение

Принимаем решение:

API создаёт заказ только из текущей API-корзины авторизованного пользователя.

Endpoint:

POST /api/orders/

используется как команда checkout текущей корзины.

API не принимает список товаров и количеств для создания заказа напрямую.

Недопустимый payload:

{
  "items": [
    {
      "product_id": 10,
      "quantity": 2
    }
  ]
}

Причина:

Позиции заказа должны проходить через корзину и её service-layer,
а не передаваться напрямую в endpoint создания заказа.

API checkout должен использовать те же бизнес-правила, что и web checkout:

- актуальные цены берутся из Product;
- остатки проверяются на момент создания заказа;
- товары блокируются через select_for_update();
- создание заказа атомарное;
- создаётся mock-payment;
- после успешного создания заказа корзина очищается;
- при ошибке заказ не создаётся и корзина не очищается.
Авторизация

Создание заказа через API доступно только авторизованному пользователю.

POST /api/orders/ требует JWT.

Если JWT отсутствует или невалиден:

401 Unauthorized

API не поддерживает guest checkout на этапе MVP.

Это согласуется с ADR 0025, где API-корзина доступна только авторизованным пользователям и работает только с DB-cart.

Источник позиций заказа

Источник позиций заказа:

Текущая DB-корзина авторизованного пользователя.

Порядок работы API checkout:

1. API получает JWT-пользователя.
2. API получает актуальный CartSnapshot через apps/cart/services.py.
3. API проверяет, что корзина не пустая.
4. API проверяет, что snapshot можно оформить: can_checkout=True.
5. API валидирует контактные и delivery-данные.
6. API вызывает orders.services.create_order_from_cart().
7. Service-layer атомарно создаёт Order, OrderItem и mock Payment.
8. После успешного создания заказа корзина очищается.
9. API возвращает созданный заказ.
Payload создания заказа

Endpoint:

POST /api/orders/
Authorization: Bearer <token>
Content-Type: application/json

Минимальный payload MVP:

{
  "customer_name": "Иван Иванов",
  "customer_email": "ivan@example.com",
  "customer_phone": "+79990000000",
  "shipping_address": "Москва, ул. Примерная, д. 1",
  "comment": "Позвонить перед доставкой"
}

Обязательные поля:

customer_name
customer_email
customer_phone
shipping_address

Необязательные поля:

comment

Если в текущей модели заказа используются другие имена полей, serializer должен соответствовать фактической модели, но публичный смысл контракта остаётся тем же:

API принимает контактные данные покупателя и адрес доставки,
но не принимает позиции заказа напрямую.
Канонический endpoint

Для этапа 12 принимается endpoint:

POST /api/orders/

Смысл endpoint:

Создать заказ из текущей корзины пользователя.

Это не generic CRUD-create заказа из произвольного payload.

Это checkout-команда.

Поэтому API-view может быть реализована отдельно от обычного OrderViewSet.create(), если это упростит контроль бизнес-логики.

Допустимые варианты реализации:

- OrderViewSet.create() как checkout-команда;
- отдельная OrderCreateAPIView;
- отдельный action внутри OrderViewSet.

Рекомендуемый вариант для MVP:

OrderViewSet.create() вызывает checkout service и создаёт заказ из корзины.

При этом serializer не должен принимать items.

Поведение после успешного создания заказа

После успешного создания заказа:

- создаётся Order;
- создаются OrderItem;
- создаётся mock Payment;
- заказ получает статус согласно web checkout, например paid;
- корзина пользователя очищается;
- API возвращает 201 Created.

Формат ответа:

{
  "id": 123,
  "status": "paid",
  "total_price": "179980.00",
  "customer_name": "Иван Иванов",
  "customer_email": "ivan@example.com",
  "customer_phone": "+79990000000",
  "shipping_address": "Москва, ул. Примерная, д. 1",
  "comment": "Позвонить перед доставкой",
  "items": [
    {
      "product": {
        "id": 10,
        "slug": "iphone-15",
        "name": "iPhone 15"
      },
      "quantity": 2,
      "unit_price": "89990.00",
      "total_price": "179980.00"
    }
  ],
  "payment": {
    "id": 555,
    "status": "paid",
    "provider": "mock"
  },
  "created_at": "2026-05-18T10:00:00Z"
}

Если mock-payment в текущей модели имеет другие поля, response serializer должен отражать фактическую модель, но контракт должен явно показывать:

- заказ создан;
- позиции зафиксированы;
- платёж создан;
- статус заказа известен клиенту.
Ошибки
Пустая корзина

Если корзина пуста:

400 Bad Request

Пример:

{
  "detail": "Нельзя создать заказ из пустой корзины."
}
В корзине есть недоступные позиции

Если CartSnapshot.can_checkout=False:

400 Bad Request

Пример:

{
  "detail": "Корзина содержит товары, недоступные для оформления.",
  "warnings": [
    "Некоторые товары в корзине сейчас недоступны для оформления."
  ]
}
Нехватка остатков при атомарном создании

Если остаток изменился между просмотром корзины и созданием заказа:

409 Conflict

Пример:

{
  "detail": "Недостаточно товара на складе для оформления заказа.",
  "code": "insufficient_stock"
}

Допустимо на MVP вернуть 400 Bad Request, но предпочтительный контракт:

409 Conflict

Причина: запрос был валиден, но состояние ресурса изменилось.

Невалидные контактные данные

Если payload не прошёл serializer validation:

400 Bad Request

Пример:

{
  "customer_email": [
    "Введите корректный адрес электронной почты."
  ],
  "shipping_address": [
    "Это поле обязательно."
  ]
}
Неавторизованный пользователь
401 Unauthorized
Использование service-layer

API checkout обязан использовать существующие доменные сервисы.

API-view не должен:

- создавать Order напрямую;
- создавать OrderItem напрямую;
- создавать Payment напрямую;
- уменьшать stock_quantity напрямую;
- очищать Cart/CartItem напрямую;
- пересчитывать total_price напрямую;
- обходить CartSnapshot.

API-view должен:

- валидировать API payload;
- получить CartSnapshot через cart service;
- вызвать order/checkout service;
- преобразовать результат в HTTP response.

Основной доменный вызов:

orders.services.create_order_from_cart(...)

Если текущая функция принимает CartSnapshot, API должен подготовить snapshot тем же способом, что и web checkout.

Атомарность

Создание заказа через API должно быть атомарным.

Правило:

Если заказ не создан полностью, система не должна оставить частично созданные OrderItem, Payment или очищенную корзину.

Внутри service-layer должна использоваться транзакция:

transaction.atomic()

Проверка и изменение остатков должны выполняться с блокировкой товаров:

select_for_update()

Это поведение должно совпадать с web checkout.

Mock Payment

На этапе MVP API использует то же mock-payment поведение, что и web checkout.

Правило:

POST /api/orders/ создаёт заказ и mock-платёж в рамках одной checkout-операции.

API не создаёт отдельный внешний payment flow.

Если в будущем появится настоящий payment provider, это должно быть оформлено отдельным ADR.

Очистка корзины

После успешного создания заказа API должен очистить DB-корзину пользователя.

Если создание заказа завершилось ошибкой:

корзина не очищается.

Это важно для UX API-клиента: пользователь сможет исправить проблему и повторить checkout.

Последствия

Плюсы решения:

- API не обходит правила корзины;
- web checkout и API checkout используют общий service-layer;
- остатки, цены и доступность проверяются одинаково;
- проще тестировать и документировать checkout;
- клиентский API контракт понятен: сначала наполнить корзину, потом создать заказ;
- заказ не создаётся из произвольного списка товаров;
- меньше риск расхождения web и API поведения;
- mock-payment поведение единообразно.

Минусы решения:

- API-клиент не может создать заказ одним запросом со списком товаров;
- перед checkout нужно сначала наполнить API-корзину;
- endpoint `POST /api/orders/` является не чистым CRUD-create, а checkout-командой;
- для B2B или интеграционного API в будущем может потребоваться отдельный bulk/order endpoint.
Связанные документы / файлы / настройки
- docs/api.md
- docs/architecture.md
- docs/conflicts.md
- docs/decisions/0026-api-order-create-contract.md
- docs/decisions/0023-api-architecture-boundary.md
- docs/decisions/0025-api-cart-contract.md
- apps/api/views/orders.py
- apps/api/serializers/orders.py
- apps/api/tests/test_orders_api.py
- apps/cart/services.py
- apps/cart/models.py
- apps/orders/services.py
- apps/orders/models.py
- apps/payments/models.py
Инварианты для реализации
1. POST /api/orders/ требует JWT.
2. API создаёт заказ только из текущей DB-корзины пользователя.
3. API не принимает items в payload создания заказа.
4. API использует CartSnapshot.
5. API использует orders.services.create_order_from_cart().
6. API checkout использует те же правила, что web checkout.
7. Создание заказа выполняется атомарно.
8. Остатки товаров проверяются под select_for_update().
9. После успешного заказа создаётся mock Payment.
10. После успешного заказа корзина очищается.
11. При ошибке создания заказа корзина не очищается.
12. Пустая корзина возвращает 400.
13. Недоступные позиции в корзине возвращают 400.
14. Конфликт остатков во время создания заказа возвращает 409 или согласованный 400.
15. API-view не создаёт Order, OrderItem и Payment напрямую.
Пример API serializer
# apps/api/serializers/orders.py

from rest_framework import serializers


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer входных данных API checkout.

    Не принимает items.
    Позиции заказа берутся из текущей корзины пользователя.
    """

    customer_name = serializers.CharField(max_length=255)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=32)
    shipping_address = serializers.CharField()
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )
Пример API view
# apps/api/views/orders.py

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.orders import OrderCreateSerializer
from apps.cart import services as cart_services
from apps.orders import services as order_services


class OrderCreateAPIView(APIView):
    """
    API checkout текущей корзины пользователя.

    Создаёт заказ только из DB-cart авторизованного пользователя.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_snapshot = cart_services.get_cart_snapshot(request)

        if cart_snapshot["is_empty"]:
            return Response(
                {
                    "detail": "Нельзя создать заказ из пустой корзины.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not cart_snapshot["can_checkout"]:
            return Response(
                {
                    "detail": "Корзина содержит товары, недоступные для оформления.",
                    "warnings": cart_snapshot.get("warnings", []),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = order_services.create_order_from_cart(
            user=request.user,
            cart_snapshot=cart_snapshot,
            customer_name=serializer.validated_data["customer_name"],
            customer_email=serializer.validated_data["customer_email"],
            customer_phone=serializer.validated_data["customer_phone"],
            shipping_address=serializer.validated_data["shipping_address"],
            comment=serializer.validated_data.get("comment", ""),
        )

        if not result["ok"]:
            return Response(
                {
                    "detail": result["error"],
                    "code": result.get("code"),
                },
                status=status.HTTP_409_CONFLICT
                if result.get("code") == "insufficient_stock"
                else status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            result["order"],
            status=status.HTTP_201_CREATED,
        )
Пример URL
# apps/api/urls.py

from django.urls import path

from apps.api.views import orders as order_views

app_name = "api"

urlpatterns = [
    path(
        "orders/",
        order_views.OrderCreateAPIView.as_view(),
        name="order-create",
    ),
]

Если используется OrderViewSet, то POST /api/orders/ должен иметь тот же смысл: checkout текущей корзины.

Пример тестовых ожиданий
1. POST /api/orders/ без JWT возвращает 401.
2. POST /api/orders/ с пустой корзиной возвращает 400.
3. POST /api/orders/ не принимает items как источник заказа.
4. POST /api/orders/ с валидной корзиной создаёт Order.
5. POST /api/orders/ создаёт OrderItem из текущей корзины.
6. POST /api/orders/ создаёт mock Payment.
7. После успешного POST /api/orders/ DB-cart очищается.
8. При ошибке валидации contact/shipping данных заказ не создаётся.
9. При ошибке checkout корзина не очищается.
10. При нехватке остатков заказ не создаётся.
11. При нехватке остатков возвращается 409 или согласованный 400.
12. API checkout использует orders.services.create_order_from_cart().
13. API-view не создаёт OrderItem напрямую.
14. API response содержит созданный заказ, позиции и payment status.
15. Web checkout и API checkout используют одинаковые бизнес-правила.
Примечание по будущему развитию

Если в будущем потребуется API для создания заказа из переданного списка товаров, это должен быть отдельный endpoint и отдельный ADR.

Возможные будущие варианты:

POST /api/order-drafts/
POST /api/integration/orders/
POST /api/b2b/orders/

Но для публичного MVP действует правило:

Клиент сначала работает с API-корзиной,
затем создаёт заказ из текущей корзины через POST /api/orders/.
