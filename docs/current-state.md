# Текущее состояние проекта

Дата оценки: 2026-05-24.

## Статус

Проект находится в состоянии функционального MVP интернет-магазина. Основные пользовательские сценарии реализованы: каталог, карточка товара, корзина, checkout, личный кабинет, отзывы, REST API, админка, demo-data, CI и базовый production runtime.

Этап 28 исключён из текущего scope. Этапы 29-30 реализованы: добавлены GitHub Actions CI и production runtime на Gunicorn, Nginx и certbot.

## Реализовано

- Домен разделён на приложения `users`, `catalog`, `cart`, `orders`, `reviews`, `payments`, `payment_emulator`, `api`.
- Web-интерфейс покрывает главную страницу, каталог, карточку товара, корзину, checkout, регистрацию, вход, профиль и заказы.
- Корзина работает через session для гостя и через DB для авторизованного пользователя.
- Checkout создаёт заказ в транзакции, повторно проверяет остатки и списывает товары только при успешной оплате.
- Payment emulator возвращает исходы `succeeded`, `failed`, `cancelled`, `pending` с заданными весами.
- Email-уведомления после checkout отправляются в режиме best-effort.
- Отзывы создаются только при подтверждённой покупке и проходят модерацию.
- REST API использует JWT, единый error contract и compatibility routes.
- Swagger/OpenAPI подключён через drf-spectacular.
- Demo-data создаётся через `seed_demo_data`; пароли не хранятся в репозитории.
- Django Admin расширен branding, dashboard, actions и аналитикой.
- Runtime UI и demo-data русскоязычные, технические ключи остаются ASCII.
- CI выполняет проверки Django, миграций, Ruff, mypy, pytest и сборку Docker images.
- Production runtime отделён от dev runtime.
- Production deploy готовится через self-hosted GitHub Actions runner для домена `myshop.iiitopm.ru`.

## Проверенный baseline

Последние проверки на 2026-05-24:

- `python manage.py check` — проходит.
- `python manage.py makemigrations --check --dry-run` — `No changes detected`.
- `python manage.py collectstatic --dry-run --noinput --clear` — проходит.
- `ruff check . --no-cache` — проходит.
- `mypy src` — проходит.
- `pytest -q -p no:cacheprovider` — `190 passed`, coverage `89%`.
- `docker compose config` — проходит.
- `docker compose -f docker-compose.prod.yml config` — проходит.
- Dev и production Docker images собираются.
- В собранные Docker images не попадают `.env` и `.env.example`.

## Ограничения

- Полная HTTPS-проверка требует внешний домен, DNS и доступные порты 80/443.
- GitHub Actions и production deploy подтверждаются после push или ручного запуска workflow.
- Повторная оплата уже созданного неоплаченного заказа не выделена в отдельный пользовательский сценарий.
- API versioning пока не вводился.

## Следующий шаг

Закрыть финальную стабилизацию:

1. Пройти clean-run по README на чистой базе.
2. Проверить UI вручную после seed-demo данных.
3. Проверить CI и deploy workflow после push/PR или ручного запуска.
4. Зафиксировать финальный release baseline в документации.
