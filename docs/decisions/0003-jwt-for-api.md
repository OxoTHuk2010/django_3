# ADR 0003: Использовать JWT для REST API

## Статус

Принято.

## Контекст

Проект должен иметь REST API для товаров, заказов, корзины, пользователей и отзывов. API должен поддерживать авторизацию независимо от web session.

## Решение

Использовать SimpleJWT для API-авторизации.

Основные endpoints:

- `POST /api/token/`
- `POST /api/token/refresh/`

## Последствия

Плюсы:

- подходит для REST API;
- не требует server-side session для API-клиентов;
- хорошо интегрируется с DRF.

Минусы:

- нужно тестировать права доступа;
- нужно аккуратно настраивать срок жизни токенов;
- token obtain flow использует `username` и `password`, потому что ADR 0007 оставляет стандартный Django login по `username`.

## Связанные настройки

- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`
- `SIMPLE_JWT`
