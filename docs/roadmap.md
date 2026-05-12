# Roadmap

Roadmap фиксирует текущий прогресс и следующие шаги. Основные документы (`README`, `architecture`, `database`, `business-rules`) описывают целевую систему, а не журнал текущих ошибок.

## Легенда

- `[x]` сделано
- `[ ]` не сделано
- `[!]` требует решения перед переходом дальше

## Последняя проверка

### Локальная проверка

Дата проверки: 2026-05-13.

- [x] `.venv\Scripts\poetry.exe run python manage.py check` — проходит, `System check identified no issues (0 silenced)`.
- [x] `.venv\Scripts\python.exe -m ruff check . --no-cache` — проходит, `All checks passed!`.
- [x] `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` — проходит, `51 passed`, покрытие `95%`.

### Docker-проверка

Дата проверки: 2026-05-12.

- [x] `docker compose up -d --build` — контейнеры пересобраны и запущены.
- [x] `docker compose ps` — `db` healthy, `web` up, порт `8000` опубликован.
- [x] `docker compose exec -T web python manage.py check` — проходит внутри контейнера.
- [x] `docker compose exec -T web python manage.py makemigrations --check --dry-run` — проходит, `No changes detected`.
- [x] `docker compose exec -T web python manage.py showmigrations` — миграции `cart`, `catalog`, `orders`, `payments`, `reviews`, `users` применены.

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

### Фактически сделано

- [x] Добавлены базовые abstract-модели в `common`: `TimeStampedModel`, `ActiveModel`, `SoftDeleteModel`.
- [x] Реализована custom-модель пользователя `users.User` со стандартным `username` как основным логином.
- [x] Реализованы модели каталога: `Category`, `Product`, `ProductImage`.
- [x] В каталоге поле описания называется `description`.
- [x] Реализованы модели заказов: `Order`, `OrderItem`.
- [x] Реализованы модели отзывов: `Review`.
- [x] В `Review` используется `settings.AUTH_USER_MODEL`.
- [x] `Review.user` использует `ForeignKey`, что соответствует правилу `один пользователь — один отзыв на один товар`.
- [x] В `Review` есть ограничение рейтинга `1..5`.
- [x] В `Review` есть ограничение уникальности пары `user + product`.
- [x] Реализованы модели платежей: `Payment` со статусами, суммой, провайдером и внешним id.
- [x] Реализованы DB-модели корзины: `Cart`, `CartItem`.
- [x] ADR 0002 принимает гибридный подход к корзине: session для гостя, DB для авторизованного пользователя.
- [x] ADR 0006 принимает ограниченное использование soft delete только для `catalog.Category` и `catalog.Product`.
- [x] ADR 0007 принимает `username` как основной логин пользователя.
- [x] ADR 0008 принимает связь `Order 1 -> N Payment` с ограничением на один успешный платёж.
- [x] Добавлены constraints для цен, количества, рейтинга и сумм.
- [x] Добавлен ADR `0005-domain-model.md`.
- [x] Миграции для базовых моделей созданы.
- [x] Миграции применены в Docker PostgreSQL.
- [x] `ruff check` проходит.
- [x] `manage.py check` проходит локально и внутри Docker.
- [x] Добавлены базовые model tests для `users`, `catalog`, `cart`, `orders`, `payments`, `reviews`.


### Definition of Done этапа 4

- [x] Все concrete-модели имеют осмысленные поля.
- [x] Нет пустых concrete-моделей с `pass`.
- [x] `python manage.py check` проходит.
- [x] `ruff check .` проходит.
- [x] Решение по корзине зафиксировано в ADR и соответствует коду.
- [x] Решение по soft delete зафиксировано в ADR и соответствует коду.
- [x] Решение по основному логину пользователя зафиксировано в ADR и соответствует коду.
- [x] Решение по связи заказа и платежей зафиксировано в ADR и соответствует коду.
- [x] Связь `Review.user` соответствует бизнес-правилу отзывов.
- [x] Миграции созданы.
- [x] Миграции применяются в Docker PostgreSQL.
- [x] `docker compose exec -T web python manage.py makemigrations --check --dry-run` не показывает изменений.
- [x] `docs/database.md` соответствует модели данных.
- [x] `docs/business-rules.md` соответствует правилам домена.
- [x] Базовые model tests добавлены и проходят.

## Этап 5. Админка

Текущий этап. Базовая регистрация моделей в Django Admin уже реализована, но этап ещё не закрыт из-за недостающих admin actions и проверок этого слоя.

### Фактически сделано

- [x] Настроен `UserAdmin` для custom user model.
- [x] Настроен `CategoryAdmin`.
- [x] Настроен `ProductAdmin`.
- [x] Настроен `ProductImageInline` внутри карточки товара.
- [x] Настроен отдельный `ProductImageAdmin`.
- [x] Настроен `CartAdmin`.
- [x] Настроен `CartItemInline` внутри карточки корзины.
- [x] Настроен отдельный `CartItemAdmin`.
- [x] Настроен `OrderAdmin`.
- [x] Настроен `OrderItemInline` внутри карточки заказа.
- [x] Настроен отдельный `OrderItemAdmin`.
- [x] Настроен `ReviewAdmin`.
- [x] Настроен `PaymentAdmin`.
- [x] В `ReviewAdmin` добавлены actions для публикации, отклонения и скрытия отзывов.
- [x] `manage.py check`, `ruff check` и `pytest` проходят после реализации текущей админки.

### Что осталось до закрытия этапа 5

- [ ] Добавить actions для активации и деактивации товаров в `ProductAdmin`.
- [ ] Добавить action для отмены заказа в `OrderAdmin`.
- [ ] Добавить actions для подтверждения и отмены оплаты в `PaymentAdmin`.
- [ ] Добавить минимальные тесты admin actions, чтобы изменения статусов не проверялись только вручную.
- [ ] Проверить вручную `/admin/`: создание категории, товара, просмотр заказа, просмотр отзывов, просмотр платежей.
- [ ] После доработки обновить `docs/roadmap.md` и, если изменятся правила модерации или статусов, `docs/business-rules.md`.

### Definition of Done этапа 5

- [x] Все основные модели зарегистрированы в Django Admin.
- [x] Для основных моделей заданы `list_display`, `list_filter`, `search_fields`, `readonly_fields` и `ordering`, где это применимо.
- [x] Для связанных объектов добавлены inline-формы: изображения товара, позиции корзины, позиции заказа.
- [ ] Все запланированные admin actions реализованы.
- [ ] Admin actions покрыты минимальными тестами.
- [ ] Ручная проверка `/admin/` выполнена на актуальной БД.

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

- [x] Финализировать подход: гибридная корзина, session для гостя и DB для авторизованного пользователя.
- [ ] Реализовать session-cart для гостя.
- [ ] Реализовать DB-cart service для авторизованного пользователя.
- [ ] Реализовать merge session-cart в DB-cart после логина.
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
- [x] Pytest config.
- [ ] Mypy config.
- [x] Базовые model tests.

## Этап 16. Тестовая стратегия

- [x] Model tests.
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
