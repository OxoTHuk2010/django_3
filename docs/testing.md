# Тестирование

Документ фиксирует текущую стратегию тестирования и фактическое покрытие. Проверки должны подтверждать не только наличие кода, но и выполнение бизнес-правил проекта.

## Команды

Локально:

```powershell
.venv\Scripts\poetry.exe run python manage.py check
.venv\Scripts\python.exe -m ruff check . --no-cache
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

В Docker:

```powershell
docker compose up -d --build
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py makemigrations --check --dry-run
docker compose exec -T web python manage.py showmigrations
```

Миграции и состояние БД проверяются через актуально пересобранный `docker compose`, чтобы результат соответствовал контейнерной среде.

## Последний локальный результат

Дата проверки: 2026-05-16.

- `manage.py check` — проходит.
- `ruff check .` — проходит.
- `pytest` — `65 passed`.
- Coverage — `95%`.

## Последний Docker-результат

Дата проверки: 2026-05-16.

- `docker compose up -d --build` — проходит, `web` запущен.
- `docker compose exec -T web python manage.py check` — проходит.
- `docker compose exec -T web python manage.py makemigrations --check --dry-run` — `No changes detected`.
- `docker compose exec -T web python manage.py showmigrations catalog` — `catalog.0001_initial` применена.
- `/` — HTTP 200.
- `/products/` — HTTP 200.
- `/guides-recipes/` — HTTP 404, маршрут не входит в текущий этап.

## Что уже покрыто

### Базовые модели

Покрыты модели:

- `users.User`
- `catalog.Category`
- `catalog.Product`
- `catalog.ProductImage`
- `cart.Cart`
- `cart.CartItem`
- `orders.Order`
- `orders.OrderItem`
- `payments.Payment`
- `reviews.Review`

Проверяются:

- строковое представление моделей;
- связи между моделями;
- базовые computed properties;
- ограничения цен, количества, рейтинга и суммы;
- snapshot цены и названия товара в `OrderItem`;
- уникальность пары `user + product` для отзывов;
- статусные свойства платежей и отзывов.

### Админка

Покрыты:

- регистрация ключевых моделей в Django Admin;
- action активации товаров;
- action деактивации товаров;
- action отмены заказа;
- action подтверждения оплаты;
- action отмены оплаты;
- корректное изменение статусов и служебных полей после выполнения actions.

### Публичный каталог

Покрыты:

- главная страница `/`;
- список товаров `/products/`;
- отображение активных неудалённых товаров;
- скрытие неактивных товаров;
- скрытие soft-deleted товаров;
- скрытие товаров из неактивных категорий;
- поиск по названию, описанию и SKU;
- фильтр по категории;
- фильтр по диапазону цены;
- игнорирование некорректного значения цены в GET-параметре;
- сортировка по возрастанию цены;
- пагинация списка товаров.

## Что пока не покрыто

Эти проверки появятся после реализации соответствующих этапов:

- детальная страница товара;
- добавление товара в корзину;
- изменение количества товара в корзине;
- удаление товара из корзины;
- merge session-cart в DB-cart после логина;
- создание заказа из корзины;
- атомарность checkout;
- уменьшение остатков;
- запрет заказа сверх остатка;
- личный кабинет;
- права доступа к заказам;
- создание отзывов через сервис;
- API endpoints;
- JWT-флоу API.

## Правило добавления тестов

Для каждой новой фичи добавлять тесты в том же этапе:

- model tests — если меняется структура данных или инварианты модели;
- selector/filter tests — если появляется сложная логика чтения;
- service tests — если меняется бизнес-состояние;
- view tests — если появляется web-страница;
- API tests — если появляется endpoint.

Тесты должны содержать русские docstring-комментарии, чтобы было понятно, какое бизнес-правило проверяется.
