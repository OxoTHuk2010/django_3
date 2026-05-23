# Roadmap

Актуальный baseline проекта на 2026-05-24 вынесен в `docs/current-state.md`. Если подробный чек-лист ниже расходится с этим снимком, приоритет для планирования имеет `docs/current-state.md`, а roadmap нужно синхронизировать перед началом нового крупного этапа.

Этапы 20-25 закрыты: baseline зафиксирован, runtime UI и demo-data русскоязычные, стандартная Django Admin улучшена, аналитика вынесена в общий service layer, checkout переведён на weighted payment emulator. Следующие крупные направления: email, compatibility API, GraphQL, CI и production runtime.

Roadmap фиксирует текущий прогресс и ближайшие шаги. Основные документы (`README`, `architecture`, `database`, `business-rules`) описывают целевую систему, а этот файл показывает фактическое состояние реализации.

## Легенда

- `[x]` сделано
- `[ ]` не сделано
- `[!]` требует решения перед переходом дальше

## Последняя локальная проверка

Дата проверки: 2026-05-24.

- [x] `.venv\Scripts\poetry.exe run python manage.py check` — проходит, `System check identified no issues (0 silenced)`.
- [x] `.venv\Scripts\python.exe -m ruff check . --no-cache` — проходит, `All checks passed!`.
- [x] `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` — проходит, `179 passed`, покрытие `90%`.

## Последняя Docker-проверка

Дата проверки: 2026-05-24.

- [x] `docker compose up -d --build` — контейнеры пересобраны и запущены.
- [x] `docker compose ps` — `db` healthy, `web` up, порт `8000` опубликован.
- [x] `docker compose exec -T web python manage.py check` — проходит внутри контейнера.
- [x] `docker compose exec -T web python manage.py makemigrations --check --dry-run` — проходит, `No changes detected`.
- [x] `docker compose exec -T web python manage.py collectstatic --dry-run --noinput --clear` — проходит, storefront/admin static видны.

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


## Этап 7. Страница товара

Статус: закрыт.


- [x] Добавить URL `/products/<slug>/`.
- [x] Добавить `ProductDetailView`.
- [x] Добавить selector для получения одного публичного товара по slug.
- [x] Создать шаблон `catalog/product_detail.html`.
- [x] Показать название, описание, цену, изображение, остаток.
- [x] Если `stock_quantity = 0`, показать состояние `Нет в наличии`.
- [x] Кнопку покупки оставить неактивной до этапа корзины по ADR 0010.
- [x] Показать только опубликованные read-only отзывы и рейтинг по ADR 0011.
- [x] Показать до 3 похожих товаров из той же активной категории по ADR 0012.
- [x] Добавить тесты открытия активного товара.
- [x] Добавить тесты недоступности неактивного и soft-deleted товара.
- [x] Добавить тест товара из скрытой категории.
- [x] Добавить тесты товара с изображением и без изображения.
- [x] Добавить тесты disabled-кнопки покупки.
- [x] Добавить тесты published/unpublished отзывов и рейтинга.
- [x] Добавить тесты похожих товаров.
- [x] Обновить `docs/business-rules.md`, `docs/testing.md`, `docs/roadmap.md`.

Критерий перехода к этапу 8:

- [x] Пользователь может открыть публичную карточку товара.
- [x] Нельзя открыть скрытый товар.
- [x] Страница корректно показывает остаток и состояние отсутствия на складе.
- [x] Тесты детальной страницы проходят.

## Этап 8. Корзина

Статус: закрыт.

- [x] Принят ADR 0002: гибридная корзина, session для гостя и DB для авторизованного пользователя.
- [x] Базовые DB-модели корзины уже есть.
- [x] Принят ADR 0013: web-маршруты и HTTP-контракт корзины.
- [x] Принят ADR 0014: сервисный слой корзины.
- [x] Принят ADR 0015: merge реализуется на этапе корзины и явно подключается к пользовательскому login-flow на этапе пользователей.
- [x] Принят ADR 0016: политика количества товара.
- [x] Принят ADR 0017: нормализация недоступных товаров в session-cart.
- [x] Реализован session-cart для гостя.
- [x] Реализован DB-cart service для авторизованного пользователя.
- [x] Реализован merge session-cart в DB-cart как сервисная функция.
- [x] Реализовано добавление товара.
- [x] Реализовано удаление товара.
- [x] Реализовано изменение количества.
- [x] Реализована очистка корзины.
- [x] Реализована проверка остатков и системного лимита позиции.
- [x] Реализована нормализация битых и недоступных позиций.
- [x] Добавлена страница `/cart/`.
- [x] Добавлены POST-маршруты `add`, `update`, `remove`, `clear`.
- [x] Кнопка на странице товара заменена на POST-форму добавления в корзину.
- [x] Добавлены service tests бизнес-правил корзины.
- [x] Добавлены web tests маршрутов корзины.

Definition of Done этапа 8:

- [x] Гость может добавить товар в корзину.
- [x] Авторизованный пользователь может добавить товар в DB-корзину.
- [x] Количество можно изменить.
- [x] Позицию можно удалить.
- [x] Корзину можно очистить.
- [x] Нельзя добавить неактивный товар.
- [x] Нельзя добавить товар без остатка.
- [x] Нельзя добавить больше остатка.
- [x] Нельзя превысить системный лимит позиции.
- [x] Битые и скрытые позиции нормализуются.
- [x] Merge session-cart в DB-cart реализован и покрыт тестами.
- [x] Подключение merge к login-flow выполнено на объединённом этапе 9-10 по ADR 0015.
- [x] `manage.py check`, `ruff check` и полный `pytest` проходят локально.

## Этап 9. Checkout и заказы

Статус: закрыт как часть объединённого среза этапов 9-10.

- [x] Добавлен `orders/services.py`.
- [x] Реализован `create_order_from_cart()`.
- [x] Создание заказа выполняется внутри `transaction.atomic()`.
- [x] Товары повторно читаются и блокируются через `select_for_update()`.
- [x] Товары блокируются в стабильном порядке по `Product.id`.
- [x] Создаются `OrderItem` со snapshot цены и названия.
- [x] Остатки товаров уменьшаются после создания позиций заказа.
- [x] Первичная MVP-логика успешной mock-оплаты была реализована на этапе 9.
- [x] На этапе 25 checkout переведён на `apps.payment_emulator` с `provider="payment_emulator"`.
- [x] После успешного checkout заказ получает статус `paid`.
- [x] Корзина очищается только после успешной оплаты.
- [x] При нехватке остатков checkout работает по all-or-nothing: заказ, позиции и платёж не создаются.
- [x] Добавлены service tests checkout.
- [x] Добавлены web tests checkout.

Definition of Done этапа 9:

- [x] Авторизованный пользователь может открыть `/checkout/`.
- [x] Гость при попытке открыть `/checkout/` перенаправляется на вход.
- [x] Нельзя оформить пустую или невалидную корзину.
- [x] Заказ создаётся из текущего snapshot корзины.
- [x] `OrderItem.price` и `OrderItem.product_name` фиксируют snapshot данных товара.
- [x] Остатки уменьшаются.
- [x] Создаётся платёж через `apps.payment_emulator`.
- [x] Корзина очищается после успешного заказа.

## Этап 10. Пользователи и личный кабинет

Статус: закрыт как часть объединённого среза этапов 9-10.

- [x] Добавлена регистрация `/accounts/register/`.
- [x] Добавлен вход `/accounts/login/`.
- [x] Добавлен выход `/accounts/logout/`.
- [x] После входа session-cart объединяется с DB-корзиной пользователя.
- [x] После регистрации пользователь автоматически входит в систему.
- [x] Добавлен профиль `/account/`.
- [x] Добавлено редактирование профиля `/account/edit/`.
- [x] Добавлена смена пароля `/account/password/`.
- [x] Добавлена история заказов `/account/orders/`.
- [x] Добавлена детальная страница заказа `/account/orders/<id>/`.
- [x] Пользователь видит только свои заказы.

Definition of Done этапа 10:

- [x] Профиль закрыт для гостя.
- [x] Авторизованный пользователь открывает личный кабинет.
- [x] Регистрация создаёт пользователя и открывает личный кабинет.
- [x] Вход переносит гостевую корзину в DB-корзину.
- [x] Профиль можно отредактировать.
- [x] Чужой заказ по id недоступен.

## Этап 11. Отзывы

Статус: закрыт.

- [x] Принят ADR 0021: право оставить отзыв даёт заказ пользователя с нужным товаром в статусе `paid`, `processing`, `shipped` или `completed`.
- [x] Принят ADR 0022: форма может отображаться на `/products/<slug>/`, но POST создания отзыва обрабатывает приложение `reviews` по маршруту `/reviews/products/<slug>/add/`.
- [x] Начальный статус нового отзыва определён текущей моделью: `pending`, публичная видимость только после модерации.
- [x] Добавлен `reviews/services.py`.
- [x] Добавлен список `REVIEW_ELIGIBLE_ORDER_STATUSES` для статусов `paid`, `processing`, `shipped`, `completed`.
- [x] Реализован `user_can_review_product(user, product)` через `Order` и `OrderItem`.
- [x] Реализован `create_product_review()` с проверкой авторизации, покупки, уникальности отзыва и выставлением `is_verified_purchase=True`.
- [x] Добавлен `reviews/forms.py` для рейтинга, заголовка и текста отзыва.
- [x] Добавлен `reviews/urls.py` с маршрутом `POST /reviews/products/<slug>/add/`.
- [x] Добавлен `ProductReviewCreateView` в `reviews/views.py`.
- [x] Подключён `reviews.urls` в корневой URLConf.
- [x] На детальной странице товара показывается форма или понятное уведомление о причине недоступности отзыва.
- [x] После успешного создания отзыва пользователь возвращается на страницу товара и видит сообщение о модерации.
- [x] Добавлены service tests для права на отзыв, запрета без покупки, запрета повторного отзыва и `is_verified_purchase=True`.
- [x] Добавлены view tests для POST-маршрута создания отзыва и связи формы с namespace `reviews`.
- [x] Обновлены `docs/business-rules.md`, `docs/testing.md`, `docs/roadmap.md`.

## Этап 12. REST API

Статус: закрыт.

- [x] Закрыть `C024`: архитектура REST API и граница ответственности `apps/api`.
- [x] Закрыть `C025`: контракт `Product API`.
- [x] Закрыть `C026`: контракт API-корзины и связь с web/session-корзиной.
- [x] Закрыть `C027`: контракт создания заказа через API.
- [x] Закрыть `C028`: контракт API-регистрации и JWT после регистрации.
- [x] Закрыть `C029`: контракт `Review API`.
- [x] Закрыть `C030`: единый формат ошибок и permissions в REST API.
- [x] Разместить API-код централизованно в `apps/api` по ADR 0023.
- [x] Добавить product endpoints.
- [x] Добавить cart endpoints.
- [x] Добавить order endpoints.
- [x] Добавить auth/register endpoints.
- [x] Добавить review endpoints.
- [x] Добавить permissions и единый формат ошибок.
- [x] Добавить API tests.

## Этап 13. Swagger/OpenAPI

- [x] Базовые URLs `/api/schema/` и `/api/docs/` подключены.
- [x] Описать реальные endpoints после реализации API.
- [x] Добавить примеры JWT-запросов в README и `docs/api.md`.

## Этап 14. Документация

- [x] Документация ведётся в `docs/`.
- [x] Добавлен `docs/roadmap.md`.
- [x] Добавлен `docs/conflicts.md`.
- [x] Добавлены ADR.
- [x] README дополнен текущими web/API-функциями.
- [x] `docs/api.md` заполнен после реализации API.

## Этап 15. Качество кода

- [x] Настроен Ruff.
- [x] Настроен pytest.
- [x] Настроен coverage.
- [x] Настроен mypy в мягком режиме.
- [x] Добавлен `.pre-commit-config.yaml` с Ruff и базовыми hooks.

## Этап 16. Тестовая стратегия

- [x] Добавлены model tests.
- [x] Добавлены admin tests.
- [x] Добавлены catalog view tests.
- [x] Добавлены service tests для корзины.
- [x] Добавлены web tests для корзины.
- [x] Добавлены service tests для checkout.
- [x] Добавлены web tests для checkout.
- [x] Добавлены view tests личного кабинета.
- [x] Добавлены service tests для отзывов.
- [x] Добавлены web tests для отзывов.
- [x] Добавлены API tests.

## Этап 17. UX-полировка

- [x] Главная страница получила базовый визуальный слой.
- [x] Список товаров получил базовый визуальный слой.
- [ ] Улучшить пустые состояния после появления корзины и checkout.
- [ ] Добавить сообщения после действий пользователя.
- [ ] Проверить вручную адаптивность после расширения web-интерфейса.

## Этап 18. Seed-данные

- [x] Закрыть `C031`: политика seed-данных и использование `src/prepare/`.
- [x] Добавить management command `seed_demo_data`.
- [x] Создавать категории.
- [x] Создавать товары.
- [x] Создавать пользователей.
- [x] Создавать заказы.
- [x] Создавать отзывы.
- [x] Добавить защиту `--reset --yes` для destructive reset.
- [x] Покрыть seed-команду тестами на идемпотентность и stop-условия.

## Этап 19. Финальная проверка

- [x] `docker compose down -v`.
- [x] `docker compose up --build`.
- [x] `docker compose exec web python src/manage.py migrate`.
- [x] `docker compose exec web python src/manage.py createsuperuser`.
- [ ] `docker compose exec web python src/manage.py seed_demo_data`.
- [x] Ручная проверка web-флоу.
- [x] Ручная проверка Swagger.
- [x] Ручная проверка JWT.
- [x] Полный локальный прогон тестов.

## Следующий детализированный план доведения до ТЗ

Этот блок фиксирует следующий слой работ по доведению проекта до полного покрытия исходного ТЗ и новых требований: современный и удобный UI, обновлённая админка, аналитика, GraphQL, CI, production runtime через Nginx/Gunicorn/HTTPS, payment emulator и русскоязычные demo-данные.

### Этап 20. Актуализация требований и baseline

Статус: закрыт 2026-05-20.

- [x] Зафиксировано, что функционально уже реализованы каталог, карточка товара, корзина, checkout, личный кабинет и отзывы.
- [x] Зафиксировано, что REST API, JWT и Swagger/OpenAPI уже подключены и покрыты тестами.
- [x] Зафиксировано, что PostgreSQL и Docker Compose уже используются как базовая инфраструктура.
- [x] Зафиксировано, что `seed_demo_data` уже существует и остаётся зоной дальнейшего расширения на этапе 22.
- [x] Зафиксировано, что Ruff, pytest и coverage настроены.
- [x] Зафиксирована последняя локальная проверка: `manage.py check` проходит.
- [x] Зафиксирована последняя локальная проверка: `ruff check` проходит.
- [x] Зафиксирована последняя локальная проверка: `pytest` проходит, `159 passed`, coverage `90%`.
- [x] Отмечено, что текущий roadmap был оптимистичен: функциональный MVP готов, но production runtime, CI, payment emulator и аналитика остаются отдельными этапами.
- [x] Позже этапы аналитики и payment emulator закрыты отдельными срезами.
- [x] Список закрытых требований ТЗ вынесен в `docs/current-state.md`.
- [x] Список незакрытых требований и остаточных рисков вынесен в `docs/current-state.md`.
- [x] Добавлен сжатый индекс ADR в `docs/decisions/README.md`.
- [x] Актуализированы перегруженные ADR через раздел `Актуальная сжатая версия`.
- [x] Зафиксировано, какие следующие этапы можно выполнять без блокеров, а какие требуют ADR.

Definition of Done этапа 20:

- [x] В roadmap есть честный status snapshot.
- [x] Отдельно перечислены реализованные требования ТЗ.
- [x] Отдельно перечислены незакрытые требования ТЗ.
- [x] Понятно, какие следующие этапы закрывают каждый оставшийся пробел.
- [x] ADR-карта сжата и связана с roadmap/conflicts.

### Этап 21. Дизайн, шаблоны и статика

Статус: закрыт 2026-05-20.

- [x] `src/prepare` используется только как reference/source визуального концепта.
- [x] `src/prepare` не используется как runtime-зависимость приложения.
- [x] Конфликт `C033` зафиксирован в `docs/conflicts.md`.
- [x] Публичные CSS-стили перенесены из reference UI и адаптированы в tracked runtime-структуру `src/static/shop/css/main.css`.
- [x] Reference JS перенесён как безопасный progressive enhancement в `src/static/shop/js/main.js`: аккордеоны, фильтры и quantity controls не подменяют Django session/cart/login.
- [x] Изображения, логотип, иконки, фоновые ассеты и аватары перенесены в tracked runtime-каталог `src/static/shop/img`.
- [x] Для будущей админской статики создан tracked runtime-каталог `src/static/admin_shop/`.
- [x] Django-шаблоны разнесены по доменам: `catalog`, `cart`, `orders`, `users`.
- [x] Общий layout вынесен в `src/templates/base.html`; повторяемые карточки товара вынесены в include.
- [x] Главная, каталог, карточка товара, корзина, checkout, login/register и базовые account views приведены к reference layout: header, hero/banner, sidebar filters, product grid, cards, footer, auth forms.
- [x] Публичный бренд сохранён как `MyShop`, несмотря на исходное название шаблона Hop & Barley.
- [x] Конфликт `C032` зафиксирован в `docs/conflicts.md`.
- [x] Runtime UI использует русскоязычные тексты, title, navigation, кнопки, формы, пустые состояния и сообщения.
- [x] Ключевые страницы имеют адаптивность через общий CSS и дополнительные runtime overrides для desktop/mobile.
- [x] UX корзины и покупки улучшен: быстрый POST `В корзину` из карточек, quantity +/- controls на карточке товара и в корзине, серверная проверка остатков сохранена.
- [x] Пустые состояния каталога, корзины, заказов и отзывов оформлены в runtime UI.
- [x] Проверено, что `collectstatic --dry-run --noinput --clear` собирает перенесённую runtime-статику.

Definition of Done этапа 21:

- [x] В roadmap прописан перенос статики и шаблонов.
- [x] Указано, что `src/prepare` остаётся reference/source.
- [x] Указано, что публичное название проекта — только `MyShop`.
- [x] Runtime-шаблоны не содержат ссылок на `src/prepare`.
- [x] Все пользовательские тексты в runtime UI русскоязычные.
- [x] Runtime JS подключён через `{% static %}` и не содержит симуляции авторизации/корзины из reference-прототипа.

### Этап 22. Русскоязычные demo-данные

Статус: закрыт 2026-05-20.

- [x] `seed_demo_data` расширен после переноса reference UI.
- [x] Категории приведены к русскоязычному формату: хмель, солод, дрожжи, добавки, наборы.
- [x] Reference-набор товаров перенесён в demo-data: 12 позиций из подготовленного сайта.
- [x] Названия и описания товаров адаптированы на русском языке под бренд `MyShop`.
- [x] Reference product images перенесены в tracked `src/static/shop/img/products`.
- [x] Seed-команда копирует изображения в `MEDIA_ROOT/demo/products` и создаёт штатные `ProductImage`.
- [x] Добавлены demo-пользователи, demo-заказы, успешные платежи через `payment_emulator` и опубликованные отзывы.
- [x] Отзывы русскоязычные и создаются идемпотентно по паре user + product.
- [x] Имена покупателей, адреса доставки и комментарии к заказам приведены к русскоязычному формату.
- [x] Технические ключи оставлены ASCII: `slug`, `SKU`, `username`, `provider_payment_id`.
- [x] Добавлены demo-заказы в статусах `paid` и `completed`; расширенные demo-сценарии отмены/неуспешной оплаты можно добавить отдельным улучшением при необходимости.
- [x] Demo-данные достаточны для проверки витрины, карточек товара, заказов, отзывов и базовой аналитики.
- [x] Идемпотентность команды сохранена.
- [x] Защита destructive reset через `--reset --yes`, `DEBUG=True` и local/demo ограничения сохранена.
- [x] Тесты seed-команды обновлены под 5 категорий, 12 товаров, 12 изображений, 4 заказа и 36 отзывов.

Definition of Done этапа 22:

- [x] Demo-данные выглядят как русскоязычный магазин.
- [x] Seed остаётся идемпотентным.
- [x] Reset остаётся защищённым.
- [x] Demo-данных достаточно для проверки витрины, карточек товара, заказов и отзывов; расширенная admin/GraphQL analytics остаётся в соответствующих будущих этапах.

### Этап 23. Современная админка

Статус: закрыт 2026-05-24.

- [x] Не заменять Django Admin внешним пакетом на первом проходе.
- [x] Зафиксировать конфликт `C034` перед началом работ.
- [x] Улучшить текущий `/admin/` через шаблоны, стили и branding.
- [x] Использовать admin-концепт из `src/prepare/templates/admin` как ориентир, без runtime-зависимости от `src/prepare`.
- [x] Сохранить стандартные Django Admin CRUD-сценарии.
- [x] Сохранить существующие permissions Django Admin.
- [x] Сохранить inline forms для связанных сущностей.
- [x] Сохранить существующие admin actions.
- [x] Добавить удобную навигацию: Dashboard.
- [x] Добавить удобную навигацию: Товары.
- [x] Добавить удобную навигацию: Заказы.
- [x] Добавить удобную навигацию: Платежи.
- [x] Добавить удобную навигацию: Отзывы.
- [x] Добавить удобную навигацию: Пользователи.
- [x] Улучшить product management: поиск.
- [x] Улучшить product management: фильтры.
- [x] Улучшить product management: бейджи статусов.
- [x] Улучшить product management: быстрые действия.
- [x] Улучшить product management: переходы к созданию и редактированию.
- [x] Добавить визуальные состояния для активных, скрытых, soft-deleted, low-stock и out-of-stock товаров.
- [x] Обеспечить русскоязычный admin UI для новых шаблонов.

Реализовано:

- `src/templates/admin/base_site.html` добавляет branding и верхнюю навигацию поверх стандартного Django Admin.
- `src/templates/admin/index.html` добавляет staff dashboard с быстрыми переходами к товарам, заказам, платежам, отзывам и пользователям.
- `src/static/admin_shop/css/admin.css` содержит отдельные стили админки и не смешивается с публичным storefront UI.
- `ProductAdmin` показывает бейджи наличия, видимости и быстрые ссылки на редактирование и публичную карточку товара.
- `apps.common.admin` задаёт русскоязычные заголовки Django Admin.
- `tests/admin/test_admin_actions.py` покрывает dashboard, бейджи товара, быстрые ссылки и ранее существующие admin actions.

Definition of Done этапа 23:

- [x] Roadmap явно разделяет Django Admin CRUD и современный admin dashboard.
- [x] Прописано, что первый шаг — кастомизация существующей админки, не замена фреймворка.
- [x] Админка остаётся совместимой с текущими model admin settings.
- [x] Новые staff-only страницы не обходят Django permissions.

### Этап 24. Админская аналитика

Статус: закрыт 2026-05-24.

- [x] Добавить staff-only dashboard.
- [x] Зафиксировать конфликт `C039` перед реализацией общего слоя аналитики.
- [x] Посчитать метрику выручки.
- [x] Посчитать метрику количества заказов.
- [x] Посчитать метрику среднего чека.
- [x] Посчитать метрику новых пользователей.
- [x] Посчитать метрику оплаченных заказов.
- [x] Посчитать метрику ожидающих оплат.
- [x] Посчитать метрику неуспешных платежей.
- [x] Посчитать список товаров с низким остатком.
- [x] Посчитать топ товаров по продажам.
- [x] Посчитать список отзывов на модерации.
- [x] Добавить фильтр периода `сегодня`.
- [x] Добавить фильтр периода `7 дней`.
- [x] Добавить фильтр периода `30 дней`.
- [x] Добавить фильтр периода `всё время`.
- [x] Использовать `Order` как источник заказов и статусов.
- [x] Использовать `OrderItem` как источник товарных продаж.
- [x] Использовать `Payment` как источник статусов оплаты.
- [x] Использовать `Product` как источник остатков.
- [x] Использовать `Review` как источник модерации.
- [x] Использовать `User` как источник пользовательской активности.
- [x] Вынести расчёты в общий read/service слой, пригодный для admin dashboard и GraphQL.

Реализовано:

- `apps.common.analytics` содержит общий read/service слой аналитики.
- `/admin/` получает аналитику через `admin.site.index` extra context и остаётся защищённым штатным staff-доступом Django Admin.
- Метрики считаются ORM-агрегациями по `Order`, `OrderItem`, `Payment`, `Product`, `Review` и `User`.
- Dashboard показывает период, summary-метрики, товары с низким остатком, топ товаров по продажам и отзывы на модерации.
- Фильтр периода поддерживает `today`, `7d`, `30d`, `all`.
- Тесты покрывают доступ к dashboard и корректность ключевых агрегатов.

Definition of Done этапа 24:

- [x] Dashboard доступен только staff.
- [x] Метрики считаются ORM-агрегациями.
- [x] Есть тесты на доступ.
- [x] Есть тесты на корректность агрегатов.
- [x] Общая аналитическая логика не дублируется между admin и GraphQL.

### Этап 25. Payment Emulator

Статус: закрыт 2026-05-24.

- [x] Добавить отдельное Django-приложение `apps.payment_emulator`.
- [x] Зафиксировать конфликт `C035` перед изменением checkout.
- [x] Оставить `payments` владельцем модели `Payment`.
- [x] Ограничить ответственность `payment_emulator` симуляцией результата провайдера.
- [x] Добавить дефолтный вес `succeeded = 7`.
- [x] Добавить дефолтный вес `failed = 1`.
- [x] Добавить дефолтный вес `cancelled = 1`.
- [x] Добавить дефолтный вес `pending = 1`.
- [x] Сделать random injectable/deterministic для тестов.
- [x] Перевести checkout с always-success mock на результат emulator.
- [x] Для `succeeded`: заказ получает `paid`.
- [x] Для `succeeded`: payment получает `succeeded`.
- [x] Для `succeeded`: остатки уменьшаются.
- [x] Для `succeeded`: корзина очищается.
- [x] Для `failed`: заказ не считается оплаченным.
- [x] Для `failed`: payment получает `failed`.
- [x] Для `failed`: остатки не уменьшаются.
- [x] Для `failed`: корзина сохраняется.
- [x] Для `cancelled`: payment получает `cancelled`.
- [x] Для `cancelled`: остатки не уменьшаются.
- [x] Для `cancelled`: корзина сохраняется.
- [x] Для `pending`: заказ и payment остаются ожидающими.
- [x] Для `pending`: остатки не уменьшаются.
- [x] Для `pending`: корзина сохраняется до финального решения.
- [x] Описать поведение в `docs/business-rules.md` после реализации.
- [x] Обновить README и API-документацию после реализации.

Реализовано:

- `apps.payment_emulator` содержит weighted выбор исхода оплаты и не владеет моделью `Payment`.
- `DEFAULT_PAYMENT_OUTCOME_WEIGHTS`: `succeeded=7`, `failed=1`, `cancelled=1`, `pending=1`.
- `orders.services.create_order_from_cart()` возвращает `CheckoutResult` и очищает корзину только при успешном outcome.
- Web checkout и API checkout сохраняют корзину при `failed`, `cancelled` и `pending`.
- Service, web и API tests используют deterministic payment outcome, поэтому проверки не зависят от настоящего random.

Definition of Done этапа 25:

- [x] В roadmap зафиксированы статусы и веса.
- [x] В conflicts описан конфликт с текущим always-success mock.
- [x] Future tests не flaky.
- [x] Checkout явно различает successful и non-successful outcomes.

### Этап 26. Email-уведомления

Статус: запланирован.

- [ ] Добавить отправку email после checkout покупателю.
- [ ] Добавить отправку email после checkout администратору.
- [ ] Использовать console email backend или locmem backend в dev/test.
- [ ] Использовать SMTP через env в production.
- [ ] Сделать письма русскоязычными.
- [ ] Включить в письмо номер заказа.
- [ ] Включить в письмо статус оплаты.
- [ ] Включить в письмо сумму.
- [ ] Включить в письмо список товаров.
- [ ] Включить в письмо адрес доставки.
- [ ] Обеспечить безопасное поведение при ошибке отправки email.
- [ ] Зафиксировать email-поведение в бизнес-документации после реализации.

Definition of Done этапа 26:

- [ ] Roadmap фиксирует email как обязательный пункт ТЗ.
- [ ] Тесты используют locmem backend.
- [ ] Ошибка отправки email не ломает уже созданный заказ.

### Этап 27. REST API compatibility

Статус: запланирован.

- [ ] Зафиксировать конфликт `C036` перед расширением API.
- [ ] Сохранить существующие slug routes.
- [ ] Добавить compatibility route `GET /api/products/<int:id>/`.
- [ ] Добавить compatibility route `POST /api/users/login/`.
- [ ] Добавить совместимый `GET /api/cart/`.
- [ ] Добавить совместимый `POST /api/cart/`.
- [ ] Добавить совместимый `PATCH /api/cart/`.
- [ ] Добавить совместимый `DELETE /api/cart/`.
- [ ] Не ломать текущие tests.
- [ ] Не удалять существующие URL.
- [ ] Обновить Swagger/OpenAPI после реализации.
- [ ] Обновить `docs/api.md` после реализации.
- [ ] Добавить примеры JWT login alias.
- [ ] Добавить примеры cart compatibility payload.

Definition of Done этапа 27:

- [ ] Roadmap явно фиксирует разницу между текущим API и таблицей ТЗ.
- [ ] Будущая реализация не удаляет существующие endpoint’ы.
- [ ] Swagger показывает both current and compatibility routes.

### Этап 28. GraphQL аналитика

Статус: запланирован.

- [ ] Добавить один endpoint `/graphql/`.
- [ ] Использовать GraphQL только для аналитики.
- [ ] Запретить anonymous доступ.
- [ ] Запретить доступ обычному пользователю.
- [ ] Разрешить доступ staff-пользователю.
- [ ] Добавить query `revenue summary`.
- [ ] Добавить query `orders count`.
- [ ] Добавить query `average order total`.
- [ ] Добавить query `revenue trend`.
- [ ] Добавить query `top products`.
- [ ] Добавить query `low stock products`.
- [ ] Добавить query `repeat customers`.
- [ ] Добавить query `payment status summary`.
- [ ] Использовать общий read/service слой аналитики из этапа 24.
- [ ] Включить GraphiQL в dev.
- [ ] Выключить GraphiQL в production.
- [ ] Документировать GraphQL queries в README и `docs/api.md` после реализации.

Definition of Done этапа 28:

- [ ] Один endpoint `/graphql/`.
- [ ] Staff-only permissions.
- [ ] Есть тесты на anonymous forbidden.
- [ ] Есть тесты на non-staff forbidden.
- [ ] Есть тесты на staff allowed.
- [ ] Есть тесты на корректность агрегатов.

### Этап 29. CI

Статус: запланирован.

- [ ] Добавить GitHub Actions workflow.
- [ ] Настроить запуск на push.
- [ ] Настроить запуск на pull request.
- [ ] Поднять PostgreSQL service в CI.
- [ ] Установить зависимости.
- [ ] Выполнить `python manage.py check`.
- [ ] Выполнить `python manage.py makemigrations --check --dry-run`.
- [ ] Выполнить `ruff check`.
- [ ] Выполнить `mypy`.
- [ ] Выполнить `pytest --cov`.
- [ ] Выполнить Docker build.
- [ ] Зафиксировать coverage threshold после стабилизации.
- [ ] Документировать CI status в README после реализации.

Definition of Done этапа 29:

- [ ] CI запускается на push и pull request.
- [ ] Все базовые проверки повторяют локальный quality gate.
- [ ] PostgreSQL-зависимые тесты проходят в CI.
- [ ] Docker image собирается в CI.

### Этап 30. Production runtime

Статус: запланирован.

- [ ] Зафиксировать конфликт `C037` перед изменением инфраструктуры.
- [ ] Сохранить dev stand для запуска на текущей ПК.
- [ ] В dev stand оставить Django `runserver`.
- [ ] В dev stand оставить PostgreSQL.
- [ ] В dev stand не требовать обязательный HTTPS.
- [ ] Добавить Gunicorn для production.
- [ ] Добавить Nginx для production.
- [ ] Добавить HTTPS через Let’s Encrypt/certbot.
- [ ] Добавить `collectstatic` в production flow.
- [ ] Добавить static volume.
- [ ] Добавить media volume.
- [ ] Включить secure cookies в production.
- [ ] Настроить HSTS через env.
- [ ] Настроить HTTP to HTTPS redirect.
- [ ] Настроить `ALLOWED_HOSTS` через env.
- [ ] Настроить `CSRF_TRUSTED_ORIGINS` через env.
- [ ] Настроить proxy headers.
- [ ] Добавить deploy workflow для production-среды.
- [ ] Добавить certbot script для первого выпуска и обновления сертификатов.
- [ ] Документировать production deployment в README после реализации.

Definition of Done этапа 30:

- [ ] Roadmap разделяет dev и production сценарии.
- [ ] Production больше не использует Django `runserver`.
- [ ] Nginx закрывает сайт и отдаёт static/media.
- [ ] HTTPS работает через Let’s Encrypt/certbot.

### Этап 31. Финальная сдача

Статус: запланирован.

- [ ] Обновить README: установка.
- [ ] Обновить README: Docker.
- [ ] Обновить README: production deploy.
- [ ] Обновить README: JWT.
- [ ] Обновить README: Swagger.
- [ ] Обновить README: GraphQL.
- [ ] Обновить README: тесты.
- [ ] Обновить README: линтеры.
- [ ] Обновить README: seed demo data.
- [ ] Обновить README: admin dashboard.
- [ ] Добавить финальный checklist реализации по ТЗ.
- [ ] Отметить все закрытые пункты ТЗ.
- [ ] Описать known limitations честно.
- [ ] Проверить clean clone.
- [ ] Проверить Docker Compose.
- [ ] Проверить migrations.
- [ ] Проверить seed.
- [ ] Проверить web smoke.
- [ ] Проверить API smoke.
- [ ] Проверить Swagger.
- [ ] Проверить GraphQL.
- [ ] Проверить admin dashboard.
- [ ] Проверить CI green.

Definition of Done этапа 31:

- [ ] Проект можно проверить по README.
- [ ] Roadmap и conflicts не противоречат фактической реализации.
- [ ] Финальный checklist покрывает исходное ТЗ.
- [ ] Состояние проекта готово к сдаче преподавателю.
