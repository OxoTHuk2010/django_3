# ADR 0025: API-корзина

## Статус

Принято.

## Контекст

Web-корзина поддерживает guest session-cart, но API должен быть предсказуемым для внешних клиентов и не зависеть от browser session.

## Решение

- API-корзина требует JWT.
- API-корзина работает только с DB-cart авторизованного пользователя.
- Session-cart и merge не применяются в API.
- Основные item endpoints:
  - `GET /api/cart/`
  - `POST /api/cart/items/`
  - `PATCH /api/cart/items/<product_id>/`
  - `DELETE /api/cart/items/<product_id>/`
  - `DELETE /api/cart/clear/`
- Compatibility endpoints `POST/PATCH/DELETE /api/cart/` переиспользуют тот же service layer.

## Последствия

Плюсы:

- API-контракт не зависит от cookie/session.
- Все операции проходят через одну DB-cart модель.
- Бизнес-правила совпадают с web-корзиной.

Минусы:

- Анонимная API-корзина не поддерживается.

## Инварианты

- Нельзя добавить недоступный товар.
- Нельзя превысить остаток или системный лимит.
- После каждой операции возвращается актуальный snapshot корзины.
- Ошибки используют единый API error contract.

## Связанные документы

- `docs/api.md`
- `docs/decisions/0014-cart-service-layer.md`
- `docs/decisions/0029-api-error-permissions-contract.md`
