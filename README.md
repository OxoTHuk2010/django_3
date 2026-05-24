# MyShop

MyShop — демонстрационный интернет-магазин на Django с web-интерфейсом, REST API, JWT-аутентификацией, PostgreSQL, Docker, CI и production runtime.

Документация ведётся на русском языке. Актуальное состояние проекта фиксируется в `docs/current-state.md`, архитектурные решения — в `docs/decisions/`.

## Возможности

- Каталог товаров с поиском, фильтрами, сортировкой и пагинацией.
- Карточка товара с изображениями, остатками, рейтингом, отзывами и похожими товарами.
- Корзина для гостя через session и для авторизованного пользователя через DB.
- Checkout с транзакционным созданием заказа и повторной проверкой остатков.
- Личный кабинет: профиль, редактирование данных, смена пароля, история и детали заказов.
- Отзывы с проверкой подтверждённой покупки и модерацией.
- Эмулятор оплаты с исходами `succeeded`, `failed`, `cancelled`, `pending`.
- Email-уведомления после checkout в режиме best-effort.
- Django Admin с branding, быстрыми ссылками, actions и staff dashboard.
- REST API с JWT, Swagger/OpenAPI и compatibility routes.
- GitHub Actions CI.
- Production runtime на Gunicorn, Nginx и certbot/Let's Encrypt.

## Стек

- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- drf-spectacular
- PostgreSQL 16
- Poetry
- Docker Compose
- Ruff
- mypy
- pytest

## Структура

```text
myshop/
├── src/
│   ├── config/
│   ├── apps/
│   ├── templates/
│   ├── static/
│   └── media/
├── docs/
│   ├── decisions/
│   ├── api.md
│   ├── architecture.md
│   ├── business-rules.md
│   ├── current-state.md
│   ├── database.md
│   ├── development.md
│   ├── roadmap.md
│   └── testing.md
├── tests/
├── docker/
├── .github/workflows/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── Dockerfile.production
├── pyproject.toml
└── README.md
```

## Быстрый старт через Docker

```bash
cp .env.example .env
# Заполните SECRET_KEY, DB_USER и DB_PASSWORD в .env.
docker compose up -d --build
```

Проверка:

```bash
docker compose ps
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
```

Основные адреса:

- Web: `http://localhost:8000/`
- Admin: `http://localhost:8000/admin/`
- Каталог: `http://localhost:8000/products/`
- Корзина: `http://localhost:8000/cart/`
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Локальный запуск без Docker

Требуется доступный PostgreSQL с параметрами из `.env`.

```bash
poetry install
cp .env.example .env
# Заполните SECRET_KEY, DB_USER и DB_PASSWORD в .env.
poetry run python manage.py check
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Конфигурация

Настройки разделены на:

- `config.settings.base` — общая конфигурация;
- `config.settings.local` — локальная разработка;
- `config.settings.production` — production-конфигурация.

Основные переменные описаны в `.env.example`. Реальные значения `SECRET_KEY`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_PASSWORD`, `MYSHOP_DEMO_PASSWORD` и `LETSENCRYPT_EMAIL` не хранятся в репозитории.

Для production обязательны внешние значения секретов и корректные `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`.

## Demo-данные

```bash
python manage.py seed_demo_data
```

По умолчанию demo-пользователи создаются без пригодного для входа пароля. Если нужен вход под demo-аккаунтом, задайте пароль только локально:

```powershell
$env:MYSHOP_DEMO_PASSWORD = Read-Host "Demo password"
python manage.py seed_demo_data
```

Безопасный reset seed-owned данных:

```bash
python manage.py seed_demo_data --reset --yes
```

Команда заблокирована для production-like окружений.

## REST API

JWT:

- `POST /api/token/`
- `POST /api/token/refresh/`
- `POST /api/users/login/`

Основные endpoints:

- `GET /api/products/`
- `GET /api/products/<slug>/`
- `GET /api/products/<id>/`
- `GET /api/cart/`
- `POST /api/cart/items/`
- `POST /api/orders/`
- `GET /api/orders/`
- `POST /api/users/register/`
- `GET /api/products/<slug>/reviews/`
- `POST /api/products/<slug>/reviews/`

API-корзина, заказы и создание отзывов требуют JWT.

## Проверки качества

```bash
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run ruff check . --no-cache
poetry run mypy src
poetry run pytest -q -p no:cacheprovider
```

Миграции и состояние БД рекомендуется проверять через актуально пересобранный Docker Compose:

```bash
docker compose up -d --build
docker compose exec web python manage.py makemigrations --check --dry-run
```

## Production runtime

Production-сценарий находится в `docker-compose.prod.yml` и использует:

- `Dockerfile.production`;
- Gunicorn для Django-приложения;
- Nginx для static/media и reverse proxy;
- certbot для Let's Encrypt;
- отдельные volumes для static, media и сертификатов.

Проверка конфигурации:

```bash
docker compose -f docker-compose.prod.yml config
docker build -f Dockerfile.production -t myshop-web:production-ci .
```

Полная HTTPS-проверка требует реальный домен, DNS и открытые порты 80/443.

## Документация

- `docs/current-state.md` — текущий baseline и остаточные риски.
- `docs/architecture.md` — архитектура и границы приложений.
- `docs/database.md` — модель данных.
- `docs/business-rules.md` — бизнес-правила.
- `docs/api.md` — REST API, JWT и Swagger.
- `docs/development.md` — запуск, конфигурация и troubleshooting.
- `docs/deployment.md` — production deploy через self-hosted GitHub Actions runner.
- `docs/testing.md` — стратегия и покрытие тестами.
- `docs/roadmap.md` — этапы реализации.
- `docs/conflicts.md` — открытые архитектурные вопросы.
- `docs/decisions/` — ADR.
