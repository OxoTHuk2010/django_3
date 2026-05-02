# MyShop

MyShop - учебный проект интернет магазина на Django c web-интерфейсом, REST API, JWT-авторизацией и Swagger-документацией

## Cтек

- Python 3.12
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- PostgreSQL
- Poetry

# Структура проекта:
```
/
├── src/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── common/
│   │   ├── users/
│   │   ├── catalog/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── reviews/
│   │   ├── payments/
│   │   └── api/
│   │
│   ├── templates/
│   ├── static/
│   └── media/
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── business-rules.md
│   ├── api.md
│   ├── development.md
│   ├── testing.md
│   └── decisions/
│       ├── 0001-use-poetry.md
│       ├── 0002-session-cart.md
│       ├── 0003-jwt-for-api.md
│       └── 0004-order-transaction.md
│
├── tests/
├── docker/
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── manage.py
└── README.md
```

## Локальный запуск

```bash
poetry install
cp .env.example .env
poetry run python manage.py migrate
poetry run python manage.py runserver
```


## Документация

Дополнительная документация:

- docs/development.md — как разрабатывать
- docs/architecture.md — архитектура
- docs/api.md — API
- docs/decisions/ — принятые решения