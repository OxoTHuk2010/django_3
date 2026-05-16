# Roadmap

Roadmap фиксирует текущий прогресс и ближайшие шаги. Основные документы (`README`, `architecture`, `database`, `business-rules`) описывают целевую систему, а этот файл показывает фактическое состояние реализации.

## Легенда

- `[x]` сделано
- `[ ]` не сделано
- `[!]` требует решения перед переходом дальше

## Последняя локальная проверка

Дата проверки: 2026-05-16.

- [x] `.venv\Scripts\poetry.exe run python manage.py check` — проходит, `System check identified no issues (0 silenced)`.
- [x] `.venv\Scripts\python.exe -m ruff check . --no-cache` — проходит, `All checks passed!`.
- [x] `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` — проходит, `65 passed`, покрытие `95%`.

## Последняя Docker-проверка

Дата проверки: 2026-05-16.

- [x] `docker compose up -d --build` — контейнеры пересобраны и запущены.
- [x] `docker compose ps` — `db` healthy, `web` up, порт `8000` опубликован.
- [x] `docker compose exec -T web python manage.py check` — проходит внутри контейнера.
- [x] `docker compose exec -T web python manage.py makemigrations --check --dry-run` — проходит, `No changes detected`.
- [x] `docker compose exec -T web python manage.py showmigrations catalog` — миграция `catalog.0001_initial` применена.
- [x] `Invoke-WebRequest http://localhost:8000/` — возвращает HTTP 200.
- [x] `Invoke-WebRequest http://localhost:8000/products/` — возвращает HTTP 200.
- [x] `Invoke-WebRequest http://localhost:8000/guides-recipes/` — возвращает HTTP 404, лишний маршрут не подключён.

Правило для следующих проверок: миграции и состояние БД проверять через актуально пересобранный `docker compose`, потому что локальная БД может не отражать контейнерную среду.

## Этап 0. Цель проекта

- [x] Определена цель: интернет-магазин с web-интерфейсом, API, JWT, Swagger, PostgreSQL, Docker, Poetry, тестами и документацией.
- [x] Принят порядок: архитектура → функциональность → API → тесты → полировка.

## Этап 1. Инициализация проекта

- [x] Создан Django-проект.
- [x] Настроена структура `src/`.
- [x] Созданы приложения: `common`, `users`, `catalog`, `cart`, `orders`, `reviews`, `payments`, `api`.
- [x] Добавлены Poetry-зависимости.
- [x] Добавлены `README.md` и директория `docs/`.

## Этап 2. Настройки проекта

- [x] Настройки разделены на `base.py`, `local.py`, `production.py`.
- [x] Подключены локальные приложения.
- [x] Подключены DRF, SimpleJWT, drf-spectacular.
- [x] Добавлен `.env.example`.
- [x] Добавлена custom user model.
- [x] Добавлены Swagger/OpenAPI URLs.
- [x] Добавлен JWT token refresh endpoint.
- [x] `manage.py check` проходит локально и в Docker.

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

- [x] Добавлены abstract-модели `TimeStampedModel`, `ActiveModel`, `SoftDeleteModel`.
- [x] Реализована custom-модель пользователя `users.User`.
- [x] Реализованы модели каталога: `Category`, `Product`, `ProductImage`.
- [x] Реализованы модели корзины: `Cart`, `CartItem`.
- [x] Реализованы модели заказов: `Order`, `OrderItem`.
- [x] Реализованы модели отзывов: `Review`.
- [x] Реализованы модели платежей: `Payment`.
- [x] Добавлены constraints для цен, количества, рейтинга и суммы.
- [x] Добавлены миграции базовых моделей.
- [x] Миграции применяются в Docker PostgreSQL.
- [x] Добавлены базовые model tests для `users`, `catalog`, `cart`, `orders`, `payments`, `reviews`.
- [x] Документация моделей и бизнес-правил приведена к текущему состоянию.

## Этап 5. Админка

Статус: закрыт.

- [x] Настроен `UserAdmin`.
- [x] Настроены `CategoryAdmin`, `ProductAdmin`, `ProductImageAdmin`.
- [x] В карточку товара добавлен `ProductImageInline`.
- [x] Настроены `CartAdmin`, `CartItemAdmin`.
- [x] В карточку корзины добавлен `CartItemInline`.
- [x] Настроены `OrderAdmin`, `OrderItemAdmin`.
- [x] В карточку заказа добавлен `OrderItemInline`.
- [x] Настроены `ReviewAdmin`, `PaymentAdmin`.
- [x] В `CategoryAdmin` добавлены actions активации и деактивации категорий.
- [x] В `ProductAdmin` добавлены actions активации и деактивации товаров.
- [x] В `OrderAdmin` добавлен action отмены заказа.
- [x] В `PaymentAdmin` добавлены actions подтверждения и отмены платежей.
- [x] В `ReviewAdmin` добавлены actions публикации, отклонения и скрытия отзывов.
- [x] Добавлены минимальные тесты admin-регистрации и admin actions.
- [x] `tests/admin` проходят.

Definition of Done этапа 5:

- [x] Основные модели зарегистрированы в Django Admin.
- [x] Для основных моделей заданы `list_display`, `list_filter`, `search_fields`, `readonly_fields` и `ordering`, где это применимо.
- [x] Для связанных объектов добавлены inline-формы.
- [x] Запланированные admin actions реализованы.
- [x] Admin actions покрыты тестами.

## Этап 6. Каталог товаров

Статус: закрыт.

- [x] Добавлена главная страница `/`.
- [x] Добавлен список товаров `/products/`.
- [x] Добавлена пагинация списка товаров.
- [x] Добавлен поиск по названию, описанию и SKU.
- [x] Добавлен фильтр по категории.
- [x] Добавлен фильтр по цене.
- [x] Добавлена сортировка `newest`, `price_asc`, `price_desc`, `popular`.
- [x] Добавлен `catalog/selectors.py`.
- [x] Добавлен `catalog/filters.py`.
- [x] Queryset публичного каталога исключает неактивные и soft-deleted товары.
- [x] Queryset публичного каталога исключает товары из неактивных и soft-deleted категорий.
- [x] Добавлены шаблоны `base.html`, `catalog/home.html`, `catalog/product_list.html`.
- [x] Добавлены view tests списка товаров.

Definition of Done этапа 6:

- [x] `/` открывается.
- [x] `/products/` открывается.
- [x] Активные товары отображаются.
- [x] Неактивные и soft-deleted товары не отображаются.
- [x] Поиск работает.
- [x] Фильтр по категории работает.
- [x] Фильтр по цене работает.
- [x] Сортировка по цене работает.
- [x] Пагинация работает.
- [x] `manage.py check`, `ruff check` и полный `pytest` проходят локально.

Остаточный риск этапа 6:

- [x] Docker-проверка после текущих изменений выполнена 2026-05-16.

## Этап 7. Страница товара

Следующий этап.

Нужно сделать:

- [ ] Добавить URL `/product/<slug>/`.
- [ ] Добавить `ProductDetailView`.
- [ ] Добавить selector для получения одного публичного товара по slug.
- [ ] Создать шаблон `catalog/product_detail.html`.
- [ ] Показать название, описание, цену, изображение, остаток.
- [ ] Если `stock_quantity = 0`, показать состояние `Нет в наличии`.
- [ ] Кнопку покупки пока можно оставить неактивной до этапа корзины.
- [ ] Показать блок отзывов, если данные уже есть.
- [ ] Показать похожие товары из той же категории.
- [ ] Добавить тесты открытия активного товара.
- [ ] Добавить тесты недоступности неактивного и soft-deleted товара.
- [ ] Обновить `docs/business-rules.md`, `docs/testing.md`, `docs/roadmap.md`.

Критерий перехода к этапу 8:

- [ ] Пользователь может открыть публичную карточку товара.
- [ ] Нельзя открыть скрытый товар.
- [ ] Страница корректно показывает остаток и состояние отсутствия на складе.
- [ ] Тесты детальной страницы проходят.

## Этап 8. Корзина

- [x] Принят ADR 0002: гибридная корзина, session для гостя и DB для авторизованного пользователя.
- [x] Базовые DB-модели корзины уже есть.
- [ ] Реализовать session-cart для гостя.
- [ ] Реализовать DB-cart service для авторизованного пользователя.
- [ ] Реализовать merge session-cart в DB-cart после логина.
- [ ] Реализовать добавление товара.
- [ ] Реализовать удаление товара.
- [ ] Реализовать изменение количества.
- [ ] Реализовать проверку остатков.
- [ ] Добавить тесты бизнес-правил корзины.

## Этап 9. Checkout и заказы

- [ ] Добавить `orders/services.py`.
- [ ] Реализовать `create_order_from_cart()`.
- [ ] Использовать `transaction.atomic()`.
- [ ] Использовать `select_for_update()` для товаров.
- [ ] Создавать `OrderItem` со snapshot цены и названия.
- [ ] Уменьшать остатки.
- [ ] Создавать mock payment.
- [ ] Очищать корзину.
- [ ] Добавить tests service-layer.

## Этап 10. Пользователи и личный кабинет

- [ ] Регистрация.
- [ ] Вход.
- [ ] Выход.
- [ ] Профиль.
- [ ] Редактирование профиля.
- [ ] Смена пароля.
- [ ] История заказов.
- [ ] Детали заказа.
- [ ] Проверка доступа только к своим заказам.

## Этап 11. Отзывы

- [ ] Добавить `reviews/services.py`.
- [ ] Реализовать `user_can_review_product()`.
- [ ] Реализовать `create_review()`.
- [ ] Проверять покупку товара перед отзывом.
- [ ] Запретить второй отзыв на тот же товар.
- [ ] Добавить tests service-layer.

## Этап 12. REST API

- [ ] Разнести API-код по доменным приложениям.
- [ ] Добавить product endpoints.
- [ ] Добавить cart endpoints.
- [ ] Добавить order endpoints.
- [ ] Добавить auth/register endpoints.
- [ ] Добавить review endpoints.
- [ ] Добавить permissions.
- [ ] Добавить API tests.

## Этап 13. Swagger/OpenAPI

- [x] Базовые URLs `/api/schema/` и `/api/docs/` подключены.
- [ ] Описать реальные endpoints после реализации API.
- [ ] Добавить примеры JWT-запросов в README.

## Этап 14. Документация

- [x] Документация ведётся в `docs/`.
- [x] Добавлен `docs/roadmap.md`.
- [x] Добавлен `docs/conflicts.md`.
- [x] Добавлены ADR.
- [ ] README нужно дополнять по мере появления web/API-функций.
- [ ] `docs/api.md` нужно заполнить после реализации API.

## Этап 15. Качество кода

- [x] Настроен Ruff.
- [x] Настроен pytest.
- [x] Настроен coverage.
- [x] Настроен mypy в мягком режиме.
- [ ] Добавить pre-commit hooks, если их ещё нет в рабочем состоянии.

## Этап 16. Тестовая стратегия

- [x] Добавлены model tests.
- [x] Добавлены admin tests.
- [x] Добавлены catalog view tests.
- [ ] Добавить service tests для корзины.
- [ ] Добавить service tests для checkout.
- [ ] Добавить view tests личного кабинета.
- [ ] Добавить API tests.

## Этап 17. UX-полировка

- [x] Главная страница получила базовый визуальный слой.
- [x] Список товаров получил базовый визуальный слой.
- [ ] Улучшить пустые состояния после появления корзины и checkout.
- [ ] Добавить сообщения после действий пользователя.
- [ ] Проверить вручную адаптивность после расширения web-интерфейса.

## Этап 18. Seed-данные

- [ ] Добавить management command `seed_demo_data`.
- [ ] Создавать категории.
- [ ] Создавать товары.
- [ ] Создавать пользователей.
- [ ] Создавать заказы.
- [ ] Создавать отзывы.

## Этап 19. Финальная проверка

- [ ] `docker compose down -v`.
- [ ] `docker compose up --build`.
- [ ] `docker compose exec web python src/manage.py migrate`.
- [ ] `docker compose exec web python src/manage.py createsuperuser`.
- [ ] `docker compose exec web python src/manage.py seed_demo_data`.
- [ ] Ручная проверка web-флоу.
- [ ] Ручная проверка Swagger.
- [ ] Ручная проверка JWT.
- [ ] Полный прогон тестов.
