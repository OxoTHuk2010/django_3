# Тестирование

Документ описывает текущую стратегию и обязательные проверки качества.

## Последний результат

Дата: 2026-05-24.

- `python manage.py check` — проходит.
- `python manage.py makemigrations --check --dry-run` — `No changes detected`.
- `python manage.py collectstatic --dry-run --noinput --clear` — проходит.
- `ruff check . --no-cache` — проходит.
- `mypy src` — проходит.
- `pytest -q -p no:cacheprovider` — `190 passed`, coverage `89%`.
- Dev и production Docker images собираются.
- Production `db + web` запускаются, Gunicorn стартует.

## Команды

Локально:

```powershell
.venv\Scripts\poetry.exe run python manage.py check
.venv\Scripts\poetry.exe run python manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe -m ruff check . --no-cache
.venv\Scripts\poetry.exe run mypy src
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

В Docker:

```powershell
docker compose up -d --build
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py makemigrations --check --dry-run
docker compose config
docker compose -f docker-compose.prod.yml config
```

## Стратегия

- Модели проверяют constraints, связи, computed properties и snapshot-поля.
- Services проверяют бизнес-операции и негативные сценарии.
- Views проверяют доступность страниц, права доступа, redirects и messages.
- API tests проверяют HTTP-контракты, JWT, permissions и формат ошибок.
- Admin tests проверяют registration, actions, dashboard и staff-only сценарии.
- Infrastructure checks проверяют settings, миграции, static, Docker Compose и сборку images.

## Покрытые области

- Пользователи: регистрация, вход, профиль, смена данных, доступ к своим заказам.
- Каталог: список, поиск, фильтры, сортировка, пагинация, карточка товара, изображения, рейтинг, похожие товары.
- Корзина: session-cart, DB-cart, merge, add/update/remove/clear, нормализация недоступных позиций.
- Checkout: атомарное создание заказа, snapshot цены и названия, проверка остатков, очистка корзины только при успешной оплате.
- Payment emulator: веса исходов и deterministic random source в тестах.
- Email: отправка после checkout и сохранение заказа при ошибке email backend.
- Отзывы: право оставить отзыв, статус `pending`, запрет повторного отзыва, публичное отображение только опубликованных отзывов.
- API: products, cart, orders, users, reviews, compatibility routes, единый error contract.
- Admin: actions, dashboard, аналитика, branding и быстрые ссылки.
- Seed-data: идемпотентность, безопасный reset, отсутствие паролей в коде.

## Правила добавления тестов

- Каждое новое бизнес-правило должно иметь тест на успешный и негативный сценарий.
- Изменение публичного API требует API tests и обновления `docs/api.md`.
- Изменение модели требует проверки миграций и model tests.
- Изменение checkout, оплаты или остатков требует service tests.
- Изменение permissions требует тестов на чужой объект и неавторизованный доступ.

## Известные ограничения

- Полный HTTPS-сценарий проверяется только на окружении с реальным доменом.
- GitHub Actions подтверждается после push/PR.
- API versioning пока не реализован.
