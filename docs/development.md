# Разработка

## Установка

```bash
poetry install
cp .env.example .env
```

## Локальный запуск

```bash
poetry run python manage.py check
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Проверка:

```bash
docker compose ps
docker compose exec web python manage.py check
```

## Адреса

- Admin: `http://localhost:8000/admin/`
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Настройки

Основной settings module для разработки:

```bash
DJANGO_SETTINGS_MODULE=config.settings.local
```

Переменные окружения описаны в `.env.example`.

Основные параметры:

- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `SECURE_COOKIES`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DJANGO_SETTINGS_MODULE`

## Проверки качества

```bash
poetry run python manage.py check
poetry run ruff check .
poetry run ruff format .
poetry run pytest
```

## Миграции

Основной путь для проверки миграций и БД в проекте — через актуально пересобранный Docker Compose:

```bash
docker compose up -d --build
```

Создать миграции внутри `web`:

```bash
docker compose exec web python manage.py makemigrations
```

Применить миграции внутри `web`:

```bash
docker compose exec web python manage.py migrate
```

Проверить, что новых миграций нет:

```bash
docker compose exec web python manage.py makemigrations --check --dry-run
```

Локальный запуск миграций через Poetry допустим только если локальный PostgreSQL поднят и параметры `.env` указывают на него:

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

## Pre-commit

Установить hooks:

```bash
poetry run pre-commit install
```

Запустить вручную:

```bash
poetry run pre-commit run --all-files
```

## Troubleshooting

### `poetry` не найден

Если `poetry` не доступен глобально, можно использовать Poetry из виртуального окружения:

```bash
.venv\Scripts\poetry.exe run python manage.py check
```

### Docker-контейнер не отражает последние изменения кода

Пересобрать контейнер:

```bash
docker compose up -d --build
```

### PostgreSQL недоступен с хоста

При работе через Docker предпочтительно выполнять команды внутри контейнера:

```bash
docker compose exec web python manage.py migrate
```
