# Architecture

## Общая структура

Проект разделён на приложения:

- users — пользователи и аутентификация
- catalog — товары и категории
- cart — корзина
- orders — заказы
- reviews — отзывы
- payments — оплата
- api — API слой (routing, schema)

## Backend архитектура

Используется классическая Django-архитектура с разделением:

- models — данные
- services — бизнес-логика (будет добавляться)
- views — обработка запросов
- api — REST слой

## Аутентификация

- Web: session-based (Django auth)
- API: JWT (SimpleJWT)

Причины:
- JWT подходит для REST API
- не требует хранения сессий на сервере
- удобен для масштабирования

## API

- Django REST Framework
- OpenAPI схема через drf-spectacular
- Swagger UI доступен по `/api/docs/`

## Конфигурация

Настройки разделены:

- base.py — общие
- local.py — разработка
- production.py — production

Это позволяет:
- изолировать безопасность
- избежать ошибок деплоя

## Architecture Decision Records

Архитектурные решения фиксируются в `docs/decisions/`.

Текущие ADR:

- ADR 0001 — использование Poetry
- ADR 0002 — session-based корзина
- ADR 0003 — JWT для REST API
- ADR 0004 — транзакционное создание заказа
