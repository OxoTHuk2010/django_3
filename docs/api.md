# API

## Текущий статус

API-инфраструктура и основные доменные API endpoints этапа 12 реализованы.

Уже доступны:

- JWT token endpoint.
- JWT refresh endpoint.
- JWT login alias `/api/users/login/`.
- OpenAPI schema.
- Swagger UI.

## Принятые решения перед реализацией API

Блокирующие конфликты этапа 12 закрыты ADR:

- ADR 0023: REST API централизован в `apps/api`, доменные приложения остаются владельцами моделей и сервисов.
- ADR 0024: Product API использует `slug` как публичный lookup.
- ADR 0025: API-корзина требует JWT и работает только с DB-cart авторизованного пользователя.
- ADR 0026: API создаёт заказ только из текущей API-корзины пользователя.
- ADR 0027: API-регистрация создаёт пользователя и сразу возвращает JWT pair.
- ADR 0028: Review API использует `slug` товара и доменный service-layer отзывов.
- ADR 0029: собственные endpoints проекта используют единый JSON-формат ошибок.

## JWT

Получение access/refresh token:

```http
POST /api/token/
```

Compatibility alias:

```http
POST /api/users/login/
```

Пример тела запроса:

```json
{
  "username": "admin",
  "password": "password"
}
```

Важно: по ADR `0007-username-user-login.md` основным логином остаётся `username`. JWT token endpoint ожидает стандартную пару `username` и `password`.

Обновление access token:

```http
POST /api/token/refresh/
```

Пример:

```json
{
  "refresh": "<refresh-token>"
}
```

## Swagger и OpenAPI

Swagger UI:

```text
/api/docs/
```

OpenAPI schema:

```text
/api/schema/
```

## Реализованные endpoints

Каталог:

- `GET /api/products/`
- `GET /api/products/<slug>/`
- `GET /api/products/<id>/` — compatibility route по внутреннему id

Корзина:

- `GET /api/cart/`
- `POST /api/cart/` — compatibility add
- `PATCH /api/cart/` — compatibility update
- `DELETE /api/cart/` — compatibility remove или clear
- `POST /api/cart/items/`
- `PATCH /api/cart/items/<product_id>/`
- `DELETE /api/cart/items/<product_id>/`
- `DELETE /api/cart/clear/`

Заказы:

- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/<id>/`

Пользователи:

- `POST /api/users/register/`
- `POST /api/users/login/`

Отзывы:

- `GET /api/products/<slug>/reviews/`
- `POST /api/products/<slug>/reviews/`

## Правила доступа

- Список и карточка товаров доступны всем.
- Корзина API требует JWT.
- Заказы API требуют JWT.
- Пользователь видит только свои заказы.
- Отзыв можно создать только при выполнении бизнес-правил reviews.

## Примеры запросов

Регистрация пользователя:

```http
POST /api/users/register/
```

```json
{
  "username": "apiuser",
  "email": "apiuser@example.com",
  "password": "StrongApiPassword123"
}
```

Добавление товара в корзину:

```http
POST /api/cart/items/
Authorization: Bearer <access-token>
```

```json
{
  "product_id": 10,
  "quantity": 2
}
```

Compatibility-добавление товара:

```http
POST /api/cart/
Authorization: Bearer <access-token>
```

```json
{
  "product_id": 10,
  "quantity": 2
}
```

Compatibility-изменение количества:

```http
PATCH /api/cart/
Authorization: Bearer <access-token>
```

```json
{
  "product_id": 10,
  "quantity": 3
}
```

Compatibility-удаление позиции:

```http
DELETE /api/cart/
Authorization: Bearer <access-token>
```

```json
{
  "product_id": 10
}
```

Compatibility-очистка корзины:

```http
DELETE /api/cart/
Authorization: Bearer <access-token>
```

Создание заказа из текущей API-корзины:

```http
POST /api/orders/
Authorization: Bearer <access-token>
```

```json
{
  "customer_name": "Иван Иванов",
  "customer_email": "ivan@example.com",
  "customer_phone": "+79990000000",
  "shipping_address": "Москва, ул. Примерная, д. 1",
  "comment": "Позвонить перед доставкой"
}
```

Создание отзыва:

```http
POST /api/products/<slug>/reviews/
Authorization: Bearer <access-token>
```

```json
{
  "rating": 5,
  "title": "Отличный товар",
  "text": "Покупкой доволен."
}
```

## Текущие ограничения

- API-корзина не поддерживает анонимную session-cart.
- API-заказ создаётся только из текущей DB-корзины пользователя.
- SimpleJWT endpoints могут возвращать стандартный формат ошибок библиотеки.
- Compatibility routes добавлены поверх текущих endpoint'ов и не заменяют slug routes или `/api/cart/items/`.
- Реальная платёжная интеграция не реализована, checkout использует `apps.payment_emulator`.
- `POST /api/orders/` может создать заказ с payment outcome `succeeded`, `failed`, `cancelled` или `pending`.
- API-корзина очищается только при `succeeded`; при `failed`, `cancelled` и `pending` корзина сохраняется для повторной попытки или дальнейшего решения оплаты.
