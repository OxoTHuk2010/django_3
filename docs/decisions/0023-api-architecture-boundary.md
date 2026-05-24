# ADR 0023: Граница REST API

## Статус

Принято.

## Контекст

REST API должен быть единым внешним контрактом проекта. При этом доменные приложения остаются владельцами моделей и бизнес-логики.

## Решение

- REST API централизован в `apps/api`.
- `apps/api` владеет serializers, views/viewsets, permissions, filters, pagination, schema и routes.
- Доменные приложения владеют models, services, selectors и бизнес-правилами.
- API-слой вызывает доменные services/selectors и не дублирует бизнес-логику.
- OpenAPI schema публикуется через drf-spectacular.

## Последствия

Плюсы:

- Внешний API-контракт находится в одном месте.
- Доменные приложения не смешиваются с DRF-слоем.
- Web и API переиспользуют одну бизнес-логику.

Минусы:

- `apps/api` становится точкой координации нескольких доменов.
- Нужно следить, чтобы serializers не превращались в бизнес-слой.

## Инварианты

- Checkout API использует `orders.services`.
- Cart API использует `cart.services`.
- Review API использует `reviews.services`.
- Product API использует catalog selectors.
- Ошибки собственных endpoints приводятся к единому contract.

## Связанные документы

- `docs/api.md`
- `docs/decisions/0029-api-error-permissions-contract.md`
