# API

## Текущий статус

API-инфраструктура подключена, но доменные API endpoints ещё не реализованы.

Уже доступны:

- JWT token endpoint.
- JWT refresh endpoint.
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

## Планируемые endpoints

По принятым ADR этапа 12 будут добавляться:

- `GET /api/products/`
- `GET /api/products/<slug>/`
- `GET /api/cart/`
- `POST /api/cart/items/`
- `PATCH /api/cart/items/<product_id>/`
- `DELETE /api/cart/items/<product_id>/`
- `DELETE /api/cart/clear/`
- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/<id>/`
- `POST /api/users/register/`
- `GET /api/products/<slug>/reviews/`
- `POST /api/products/<slug>/reviews/`

## Правила доступа, которые нужно реализовать позже

- Список и карточка товаров доступны всем.
- Корзина API требует JWT.
- Заказы API требуют JWT.
- Пользователь видит только свои заказы.
- Отзыв можно создать только при выполнении бизнес-правил reviews.

## Текущие ограничения

- `apps/api/urls.py` пока пустой.
- Сериализаторы ещё не созданы.
- Permissions ещё не созданы.
- API-тесты ещё не написаны.
