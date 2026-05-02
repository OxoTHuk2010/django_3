# API

## Аутентификация

Используется JWT.

### Получение токена

POST /api/token/

```json
{
  "username": "admin",
  "password": "password"
}
```
###  Обновление токена

POST /api/token/refresh/

## Документация

Swagger UI:
```
/api/docs/
```
OpenAPI schema:
```
/api/schema/
```
## Планируемые endpoints
- /api/products/
- /api/cart/
- /api/orders/
- /api/users/
- /api/reviews/