# Roadmap

Roadmap фиксирует текущий прогресс и следующие шаги. Основные документы (`README`, `architecture`, `database`, `business-rules`) описывают целевую систему, а не журнал текущих ошибок.

## Легенда

- `[x]` сделано
- `[ ]` не сделано
- `[!]` требует решения перед переходом дальше

## Последняя проверка

Дата проверки: 2026-05-11.

Команды, выполненные по текущим файлам проекта:

- [x] `.venv\Scripts\poetry.exe run python manage.py check` — проходит, `System check identified no issues (0 silenced)`.
- [x] `.venv\Scripts\python.exe -m ruff check . --no-cache` — проходит, `All checks passed!`.
- [!] `.venv\Scripts\python.exe -m pytest --collect-only -q -p no:cacheprovider` — тесты не найдены, `no tests collected`.
- [x] `docker compose up -d --build` — контейнеры пересобраны и запущены.
- [x] `docker compose ps` — `db` healthy, `web` up, порт `8000` опубликован.
- [x] `docker compose exec -T web python manage.py check` — проходит внутри контейнера.
- [!] `docker compose exec -T web python manage.py makemigrations --check --dry-run` — показывает несозданные миграции для `catalog`, `orders`, `payments`, `reviews`, `cart`, `users`.

Правило для следующих проверок: миграции и состояние БД проверять через актуально пересобранный `docker compose`, потому что локальная БД на `localhost:5432` может не отражать состояние контейнерной среды.

## Этап 0. Цель проекта

- [x] Определена цель: интернет-магазин с web, API, JWT, Swagger, PostgreSQL, Docker, Poetry, тестами и документацией.
- [x] Принят порядок: архитектура → функциональность → API → тесты → полировка.

## Этап 1. Инициализация проекта

- [x] Создан Django-проект.
- [x] Настроена структура `src/`.
- [x] Созданы приложения: `common`, `users`, `catalog`, `cart`, `orders`, `reviews`, `payments`, `api`.
- [x] Добавлены Poetry-зависимости.
- [x] Добавлен `README.md`.
- [x] Добавлена директория `docs/`.

## Этап 2. Настройки проекта

- [x] Разделены настройки на `base.py`, `local.py`, `production.py`.
- [x] Подключены локальные приложения.
- [x] Подключены DRF, SimpleJWT, drf-spectacular.
- [x] Добавлен `.env.example`.
- [x] Добавлен custom user model.
- [x] Добавлены Swagger/OpenAPI URLs.
- [x] Добавлен JWT token refresh endpoint.
- [x] `manage.py check` проходит локально и внутри Docker.

## Этап 3. Docker и PostgreSQL

- [x] Добавлен `Dockerfile`.
- [x] Добавлен `docker-compose.yml`.
- [x] Добавлен PostgreSQL service.
- [x] Добавлен web service.
- [x] Настроен healthcheck PostgreSQL.
- [x] Web service ждёт healthy DB.
- [x] Порт `8000` опубликован наружу.
- [x] При старте web выполняет `migrate` и запускает `runserver`.
- [x] После `docker compose up -d --build` контейнер `web` остаётся в состоянии `Up`.

## Этап 4. Базовые модели

Статус: в работе.

### Фактически сделано

- [x] Добавлены базовые abstract-модели в `common`: `TimeStampedModel`, `ActiveModel`, `SoftDeleteModel`.
- [x] Реализована custom-модель пользователя `users.User` с email как основным логином.
- [x] Реализованы модели каталога: `Category`, `Product`, `ProductImage`.
- [x] В каталоге поле описания называется `description`.
- [x] Реализованы модели заказов: `Order`, `OrderItem`.
- [x] Реализованы модели отзывов: `Review`.
- [x] В `Review` используется `settings.AUTH_USER_MODEL`.
- [x] В `Review` есть ограничение рейтинга `1..5`.
- [x] В `Review` есть ограничение уникальности пары `user + product`.
- [x] Реализованы модели платежей: `Payment` со статусами, суммой, провайдером и внешним id.
- [x] Реализованы DB-модели корзины: `Cart`, `CartItem`.
- [x] Добавлены constraints для цен, количества, рейтинга и сумм.
- [x] Добавлен ADR `0005-domain-model.md`.
- [x] `ruff check` проходит.
- [x] `manage.py check` проходит локально и внутри Docker.

### Что мешает закрыть этап 4

- [!] Не принято финальное решение по корзине: исходный план и ADR 0002 описывают session cart, но в коде уже есть database-backed `Cart`/`CartItem`.
- [!] В `reviews.Review.user` сейчас `OneToOneField`. Это ограничивает пользователя одним отзывом вообще и конфликтует с правилом `один пользователь — один отзыв на один товар`.
- [!] Миграции для текущих моделей не созданы. Docker-проверка `makemigrations --check --dry-run` показывает pending migrations для `catalog`, `orders`, `payments`, `reviews`, `cart`, `users`.
- [!] Тесты пока отсутствуют: `pytest --collect-only` не находит тесты.

### Что сделать до закрытия этапа 4

1. Принять решение по корзине.
2. Если остаётся session cart: удалить DB-модели `Cart`/`CartItem` до создания миграций и оставить реализацию корзины на уровне session-сервиса.
3. Если принимается database-backed cart: обновить ADR 0002, `docs/database.md`, `docs/business-rules.md` и явно описать сценарий гостевой корзины.
4. Исправить связь `reviews.Review.user` с `OneToOneField` на `ForeignKey`, если сохраняется бизнес-правило `один пользователь — один отзыв на один товар`.
5. После архитектурных решений создать миграции внутри актуального Docker-окружения: `docker compose exec -T web python manage.py makemigrations`.
6. Применить миграции: `docker compose exec -T web python manage.py migrate`.
7. Повторить проверку: `docker compose exec -T web python manage.py makemigrations --check --dry-run`.
8. Добавить минимальные model tests для критичных ограничений или явно перенести их в этап тестирования отдельным решением.
9. Повторить `docker compose exec -T web python manage.py check` и `ruff check`.

### Definition of Done этапа 4

- [x] Все concrete-модели имеют осмысленные поля.
- [x] Нет пустых concrete-моделей с `pass`.
- [x] `python manage.py check` проходит.
- [x] `ruff check .` проходит.
- [ ] Решение по корзине зафиксировано в ADR и соответствует коду.
- [ ] Связь `Review.user` соответствует бизнес-правилу отзывов.
- [ ] Миграции созданы.
- [ ] Миграции применяются в Docker PostgreSQL.
- [ ] `docker compose exec -T web python manage.py makemigrations --check --dry-run` не показывает изменений.
- [ ] `docs/database.md` соответствует модели данных.
- [ ] `docs/business-rules.md` соответствует правилам домена.

## Этап 5. Админка

Начинать после закрытия архитектурных решений и миграций этапа 4.

- [ ] Настроить `CategoryAdmin`.
- [ ] Настроить `ProductAdmin`.
- [ ] Настроить `ProductImageInline`.
- [ ] Настроить `OrderAdmin`.
- [ ] Настроить `OrderItemInline`.
- [ ] Настроить `ReviewAdmin`.
- [ ] Настроить `PaymentAdmin`.
- [ ] Добавить actions для активации/деактивации товаров.
- [ ] Добавить actions для отмены заказа.
- [ ] Добавить actions для подтверждения или отмены оплаты.

## Этап 6. Каталог товаров

- [ ] Главная страница.
- [ ] Список товаров.
- [ ] Пагинация.
- [ ] Поиск.
- [ ] Фильтр по категории.
- [ ] Фильтр по цене.
- [ ] Сортировка.
- [ ] `catalog/selectors.py`.
- [ ] `catalog/filters.py`.
- [ ] Тесты списка товаров.

## Этап 7. Страница товара

- [ ] Детальная страница товара.
- [ ] Изображения.
- [ ] Остаток.
- [ ] Рейтинг.
- [ ] Отзывы.
- [ ] Форма добавления в корзину.
- [ ] Состояние `Нет в наличии`.

## Этап 8. Корзина

- [ ] Финализировать подход: session или DB.
- [ ] Реализовать `Cart` service.
- [ ] Добавление товара.
- [ ] Удаление товара.
- [ ] Изменение количества.
- [ ] Проверка остатков.
- [ ] Тесты бизнес-правил корзины.

## Этап 9. Checkout и заказы

- [ ] `orders/services.py`.
- [ ] `create_order_from_cart()`.
- [ ] `transaction.atomic()`.
- [ ] `select_for_update()`.
- [ ] Создание `OrderItem`.
- [ ] Уменьшение остатков.
- [ ] Создание mock payment.
- [ ] Очистка корзины.
- [ ] Тесты checkout.

## Этап 10. Пользователи и личный кабинет

- [ ] Регистрация.
- [ ] Вход.
- [ ] Выход.
- [ ] Профиль.
- [ ] Редактирование профиля.
- [ ] Смена пароля.
- [ ] История заказов.
- [ ] Детали заказа.
- [ ] Защита от просмотра чужих заказов.

## Этап 11. Отзывы

- [ ] Проверка права оставить отзыв.
- [ ] Создание отзыва.
- [ ] Запрет второго отзыва на тот же товар.
- [ ] Модерация.
- [ ] Тесты правил отзывов.

## Этап 12. REST API

- [ ] API товаров.
- [ ] API корзины.
- [ ] API заказов.
- [ ] API пользователей.
- [ ] API отзывов.
- [ ] Permissions.
- [ ] API-тесты.

## Этап 13. Swagger/OpenAPI

- [x] drf-spectacular подключён.
- [x] `/api/schema/` добавлен.
- [x] `/api/docs/` добавлен.
- [ ] Описать реальные endpoints после реализации API.

## Этап 14. Документация

- [x] README.
- [x] Architecture.
- [x] API draft.
- [x] Development guide.
- [x] Database model draft.
- [x] Business rules draft.
- [x] Testing strategy draft.
- [x] ADR.
- [x] Roadmap.
- [x] Conflicts register.
- [ ] Обновлять документацию при каждом изменении модели и бизнес-правил.

## Этап 15. Качество кода

- [x] Ruff добавлен.
- [x] Pre-commit добавлен.
- [ ] Pytest config.
- [ ] Mypy config.
- [ ] Базовые тесты.

## Этап 16. Тестовая стратегия

- [ ] Model tests.
- [ ] Service tests.
- [ ] View tests.
- [ ] API tests.

## Этап 17. UX-полировка

- [ ] Главная страница.
- [ ] Пустая корзина.
- [ ] Сообщения об ошибках.
- [ ] Сохранение фильтров при пагинации.
- [ ] Аккуратный личный кабинет.

## Этап 18. Seed-данные

- [ ] Management command `seed_demo_data`.
- [ ] Категории.
- [ ] Товары.
- [ ] Пользователи.
- [ ] Заказы.
- [ ] Отзывы.

## Этап 19. Финальная проверка

- [ ] `docker compose down -v`.
- [ ] `docker compose up --build`.
- [ ] `migrate`.
- [ ] `createsuperuser`.
- [ ] `seed_demo_data`.
- [ ] Ручная проверка web flow.
- [ ] Проверка Swagger.
- [ ] Проверка API JWT.
- [ ] Проверка тестов.
