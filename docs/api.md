# API

## Текущий статус

API-инфраструктура подключена, но доменные API endpoints ещё не реализованы.

Уже доступны:

- JWT token endpoint.
- JWT refresh endpoint.
- OpenAPI schema.
- Swagger UI.

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

После завершения доменной модели и web-части будут добавляться:

- `GET /api/products/`
- `GET /api/products/<id>/`
- `POST /api/cart/`
- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/<id>/`
- `POST /api/users/register/`
- `POST /api/products/<id>/reviews/`

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
