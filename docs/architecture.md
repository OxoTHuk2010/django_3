# Архитектура

MyShop — монолитный Django-проект с разделением по доменным приложениям и явными границами между HTTP-слоем, бизнес-логикой и доступом к данным.

## Приложения

- `common` — общие абстрактные модели, аналитика и переиспользуемые utilities.
- `users` — пользователь, регистрация, вход, профиль и личный кабинет.
- `catalog` — категории, товары, изображения и публичный каталог.
- `cart` — session-cart, DB-cart и операции корзины.
- `orders` — checkout, заказы, позиции заказов и email-уведомления.
- `reviews` — отзывы, проверка права оставить отзыв и модерация.
- `payments` — модель платежа и статусы оплаты.
- `payment_emulator` — симуляция результата платёжного провайдера.
- `api` — REST API, serializers, views, permissions, schema и routes.

## Слои

- `models.py` — структура данных и базовые ограничения.
- `selectors.py` — read/query logic.
- `services.py` — бизнес-операции, изменяющие состояние.
- `forms.py` — валидация web-ввода.
- `views.py` — HTTP-слой без тяжёлой бизнес-логики.
- `admin.py` — административный интерфейс.
- `apps/api/` — внешний REST-контракт.

## Принципы

- Views вызывают services/selectors и не содержат длинную бизнес-логику.
- Checkout выполняется через service layer и транзакцию.
- API переиспользует доменные сервисы и не дублирует бизнес-правила.
- Selectors каталога скрывают неактивные и soft-deleted сущности.
- Пользовательские данные фильтруются по текущему пользователю.
- Security-sensitive значения передаются через окружение, а не через код.

## Web routes

- `/` — главная страница.
- `/products/` — список товаров.
- `/products/<slug>/` — карточка товара.
- `/cart/` — корзина.
- `/checkout/` — оформление заказа.
- `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` — auth flow.
- `/account/`, `/account/edit/`, `/account/password/`, `/account/orders/` — личный кабинет.
- `/reviews/products/<slug>/add/` — создание отзыва.
- `/admin/` — Django Admin.

## Аутентификация

- Web использует Django sessions.
- После web-login session-cart объединяется с DB-cart пользователя.
- REST API использует JWT access/refresh через SimpleJWT.
- API-корзина и API-checkout работают только с авторизованным JWT-пользователем.

## Checkout

Checkout состоит из `cart.services` и `orders.services`:

1. Корзина нормализуется и превращается в snapshot.
2. `create_order_from_cart()` открывает транзакцию.
3. Товары повторно читаются и блокируются через `select_for_update()`.
4. Создаются `Order`, `OrderItem` и `Payment`.
5. Остатки уменьшаются только при `payment.status = succeeded`.
6. Корзина очищается только при успешной оплате.
7. Email-уведомления отправляются best-effort и не откатывают заказ.

## Admin

Админка остаётся стандартным Django Admin. Кастомизация ограничена branding, шаблонами, CSS, dashboard, actions и быстрыми ссылками. Права доступа и CRUD-механика Django Admin не обходятся.

Аналитика считается в `apps.common.analytics`, а не в шаблонах. Dashboard получает агрегаты через admin context.

## REST API

REST API централизован в `apps/api`:

- products: публичный список и карточка;
- cart: JWT-only DB-cart;
- orders: JWT-only список, детали и checkout;
- users: регистрация и login alias;
- reviews: список опубликованных отзывов и создание отзыва;
- schema/docs: OpenAPI и Swagger.

Собственные API endpoints используют единый формат ошибок `{code, detail, fields}`.

## Runtime

Dev runtime:

- `docker-compose.yml`;
- Django `runserver`;
- PostgreSQL service.

Production runtime:

- `docker-compose.prod.yml`;
- `Dockerfile.production`;
- Gunicorn;
- Nginx;
- static/media volumes;
- certbot/Let's Encrypt.

Production settings требуют внешние секреты и безопасные host/origin значения.

## ADR

Архитектурные решения находятся в `docs/decisions/`. Индекс действующих решений: `docs/decisions/README.md`.
