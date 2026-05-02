# Development Guide

## Используемый стек

- Django
- Django REST Framework
- PostgreSQL
- JWT (SimpleJWT)
- Swagger (drf-spectacular)
- Poetry

## Установка

```bash
poetry install
cp .env.example .env
```

## Запуск

```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Проверка конфигурации

```bash
poetry run python manage.py check
```

## Настройки

Проект использует разделение настроек:

- config.settings.local — для разработки
- config.settings.production — для production

Переключение через переменную:

```bash
DJANGO_SETTINGS_MODULE=config.settings.local
```

## Переменные окружения

Минимальный набор:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- DB_*

См. .env.example
