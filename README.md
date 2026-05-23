# MyShop

Актуальный инженерный снимок проекта, результаты проверок и ближайшие этапы зафиксированы в `docs/current-state.md`.

MyShop — учебный проект интернет-магазина на Django. Цель проекта — собрать небольшой, аккуратный backend-продукт с веб-интерфейсом, корзиной, заказами, личным кабинетом, REST API, JWT-авторизацией, Swagger-документацией, PostgreSQL, Docker, Poetry, тестами и понятной инженерной документацией.

## Возможности

Планируемая функциональность:

- каталог товаров и категорий;
- страница товара с изображениями, остатками, рейтингом и отзывами;
- корзина для гостя через session и для авторизованного пользователя через DB;
- оформление заказа для авторизованного пользователя;
- регистрация, вход, профиль, смена пароля и история заказов;
- отзывы на товары;
- эмулятор оплаты с успешными, неуспешными, отменёнными и ожидающими исходами;
- современная админка на базе стандартного Django Admin;
- админская аналитика на `/admin/`;
- REST API;
- JWT-авторизация для API;
- Swagger/OpenAPI документация;
- Docker Compose окружение с PostgreSQL.

## Стек

- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- drf-spectacular
- PostgreSQL
- Poetry
- Docker Compose
- Ruff
- pytest

## Структура проекта

```text
myshop/
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
│   │   ├── payment_emulator/
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
│   ├── roadmap.md
│   ├── conflicts.md
│   └── decisions/
│       ├── 0001-use-poetry.md
│       ├── 0002-session-cart.md
│       ├── 0003-jwt-for-api.md
│       ├── 0004-order-transaction.md
│       ├── 0005-domain-model.md
│       ├── 0006-soft-delete.md
│       ├── 0007-username-user-login.md
│       ├── 0008-payment-order.md
│       ├── 0009-img-source.md
│       ├── 0010-button.md
│       ├── 0011-reviews-rating.md
│       ├── 0012-rule-product.md
│       ├── 0013-cart-web-routes.md
│       ├── 0014-cart-service-layer.md
│       ├── 0015-cart-merge-timing.md
│       ├── 0016-cart-quantity-policy.md
│       ├── 0017-session-cart-invalid-products.md
│       ├── 0021-review-eligible-order-status.md
│       ├── 0022-review-web-create-contract.md
│       ├── 0023-api-architecture-boundary.md
│       ├── 0024-product-api-contract.md
│       ├── 0025-api-cart-contract.md
│       ├── 0026-api-order-create-contract.md
│       ├── 0027-api-registration-jwt.md
│       ├── 0028-review-api-contract.md
│       ├── 0029-api-error-permissions-contract.md
│       ├── 0030-seed-data-policy.md
│       ├── 0031-myshop-brand-and-runtime-assets.md
│       ├── 0032-admin-ui-and-dashboard.md
│       ├── 0033-payment-emulator.md
│       ├── 0034-api-compatibility-routes.md
│       ├── 0035-production-runtime.md
│       ├── 0036-russian-demo-data.md
│       └── 0037-analytics-service-layer.md
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

Локальный запуск предполагает, что PostgreSQL доступен по параметрам из `.env`.

```bash
poetry install
cp .env.example .env
poetry run python manage.py check
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Проверка контейнеров:

```bash
docker compose ps
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
```

## Основные адреса

- Admin: `http://localhost:8000/admin/`
- Каталог: `http://localhost:8000/products/`
- Корзина: `http://localhost:8000/cart/`
- Checkout: `http://localhost:8000/checkout/`
- Вход: `http://localhost:8000/accounts/login/`
- Регистрация: `http://localhost:8000/accounts/register/`
- Личный кабинет: `http://localhost:8000/account/`
- История заказов: `http://localhost:8000/account/orders/`
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## REST API

Основные endpoints:

- `GET /api/products/`
- `GET /api/products/<slug>/`
- `GET /api/cart/`
- `POST /api/cart/items/`
- `POST /api/orders/`
- `GET /api/orders/`
- `POST /api/users/register/`
- `GET /api/products/<slug>/reviews/`
- `POST /api/products/<slug>/reviews/`

API-корзина, заказы и создание отзывов требуют JWT.

## Demo-данные

```bash
python manage.py seed_demo_data
```

Безопасный reset demo-данных:

```bash
python manage.py seed_demo_data --reset --yes
```

## Конфигурация

Настройки разделены на:

- `config.settings.base` — общие настройки;
- `config.settings.local` — локальная разработка;
- `config.settings.production` — production-настройки.

Основные переменные окружения описаны в `.env.example`.

## Документация

- `docs/current-state.md` — текущий baseline проекта, проверки, остаточные риски и ближайшие реализуемые этапы.
- `docs/architecture.md` — архитектура проекта и ответственность приложений.
- `docs/database.md` — модель данных и связи между сущностями.
- `docs/business-rules.md` — бизнес-правила домена.
- `docs/api.md` — API, JWT и Swagger.
- `docs/development.md` — запуск, конфигурация и troubleshooting.
- `docs/testing.md` — стратегия тестирования.
- `docs/roadmap.md` — чек-лист этапов проекта: сделано и предстоит.
- `docs/conflicts.md` — текущие и закрытые архитектурные конфликты.
- `docs/decisions/` — ADR: архитектурные решения.

## Проверки качества

```bash
poetry run ruff check .
poetry run ruff format .
poetry run pytest
```

## Статус разработки

Текущий прогресс и список следующих задач ведутся в `docs/roadmap.md`. Архитектурные противоречия фиксируются отдельно в `docs/conflicts.md`.

На текущем этапе реализованы публичные web-страницы:

- `/` — главная страница;
- `/products/` — список товаров;
- `/products/<slug>/` — детальная страница товара;
- `/cart/` — корзина;
- `/checkout/` — оформление заказа для авторизованного пользователя;
- `/account/` — личный кабинет;
- `/account/orders/` — история заказов.

Текущие локальные проверки: `manage.py check`, `ruff check` и `pytest` проходят; последний полный прогон фиксируется в `docs/testing.md`.
