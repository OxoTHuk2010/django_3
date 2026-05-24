# ADR 0029: API errors и permissions

## Статус

Принято.

## Контекст

Собственные API endpoints должны возвращать предсказуемые ошибки. Пользователь не должен отличать несуществующий чужой объект от недоступного по правам.

## Решение

Собственные endpoints проекта возвращают ошибки в формате:

```json
{
  "code": "error_code",
  "detail": "Описание ошибки.",
  "fields": {}
}
```

Правила доступа:

- Чужие заказы скрываются через 404.
- API-корзина и заказы требуют JWT.
- Создание отзывов требует JWT и подтверждённой покупки.
- SimpleJWT endpoints могут сохранять стандартный формат ошибок библиотеки.

## Последствия

Плюсы:

- Клиент получает единый contract для ошибок проекта.
- Permissions не раскрывают наличие чужих объектов.
- Бизнес-ошибки можно обрабатывать по `code`.

Минусы:

- Нужно поддерживать адаптер ошибок поверх DRF validation/service errors.
- Ошибки сторонних endpoints могут отличаться.

## Основные коды

- `authentication_required`
- `permission_denied`
- `not_found`
- `validation_error`
- `cart_empty`
- `cart_has_unavailable_items`
- `insufficient_stock`
- `review_not_allowed`
- `review_already_exists`

## Инварианты

- Не возвращать traceback или внутренние детали реализации.
- Не раскрывать существование чужих заказов.
- Field errors должны быть помещены в `fields`.
- Общий текст ошибки должен быть в `detail`.

## Связанные документы

- `docs/api.md`
- `docs/decisions/0023-api-architecture-boundary.md`
