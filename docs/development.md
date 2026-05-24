# Разработка

## Требования

- Python 3.12
- Poetry
- Docker и Docker Compose
- PostgreSQL 16 для локального запуска без Docker

## Настройка окружения

```bash
poetry install
cp .env.example .env
```

Заполните в `.env` как минимум:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Секреты не хранятся в репозитории. Для production используйте переменные окружения или secrets-хранилище платформы.

## Локальный запуск

```bash
poetry run python manage.py check
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Проверка:

```bash
docker compose ps
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
```

Миграции и состояние БД предпочтительно проверять через актуально пересобранный Docker Compose.

## Quality gates

```bash
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run ruff check . --no-cache
poetry run mypy src
poetry run pytest -q -p no:cacheprovider
```

Если тесты запускаются с host-машины против PostgreSQL из Docker, используйте `DB_HOST=localhost`. Внутри контейнера используется `DB_HOST=db`.

## Миграции

Создать миграции внутри контейнера:

```bash
docker compose exec web python manage.py makemigrations
```

Применить миграции:

```bash
docker compose exec web python manage.py migrate
```

Проверить отсутствие незакоммиченных миграций:

```bash
docker compose exec web python manage.py makemigrations --check --dry-run
```

## Demo-данные

```bash
python manage.py seed_demo_data
```

Для demo-пользователей пароль задаётся только через окружение:

```powershell
$env:MYSHOP_DEMO_PASSWORD = Read-Host "Demo password"
python manage.py seed_demo_data
```

Если `MYSHOP_DEMO_PASSWORD` не задан, demo-пользователи создаются с unusable password.

Reset seed-owned данных:

```bash
python manage.py seed_demo_data --reset --yes
```

Команда reset заблокирована для production-like окружений.

## Production runtime

Production-сценарий отделён от dev-сценария:

- dev: `docker-compose.yml`, Django `runserver`;
- production: `docker-compose.prod.yml`, Gunicorn, Nginx, certbot, static/media volumes.

Проверка production compose:

```bash
docker compose -f docker-compose.prod.yml config
```

Сборка production image:

```bash
docker build -f Dockerfile.production -t myshop-web:production-ci .
```

Проверка `db + web` без HTTPS:

```bash
docker compose -f docker-compose.prod.yml up -d --build db web
docker compose -f docker-compose.prod.yml exec web python manage.py check
```

Полная HTTPS-проверка требует домен, DNS и открытые порты 80/443.

Production deploy через GitHub Actions описан в `docs/deployment.md`.

## Pre-commit

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Troubleshooting

### `poetry` не найден

Используйте Poetry из виртуального окружения:

```powershell
.venv\Scripts\poetry.exe run python manage.py check
```

### Контейнер не видит свежие изменения

```bash
docker compose up -d --build
```

### Локальные тесты не подключаются к БД

Проверьте `DB_HOST`. Для host-машины обычно нужен `localhost`, для контейнера — `db`.

### Production settings не стартуют

Проверьте обязательные переменные: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
