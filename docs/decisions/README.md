# ADR index

Этот индекс сжимает действующие архитектурные решения и связывает их с актуальной картой `docs/roadmap.md` и конфликтами `docs/conflicts.md`. Полные ADR остаются историческим журналом, но при реализации следует сначала смотреть на этот индекс, затем на конкретный ADR.

## Правило актуальности

- ADR `0001`-`0037` считаются принятыми и действующими, если ниже не указано ограничение.
- Конфликты `C032`-`C039` закрыты ADR `0031`-`0037`; при реализации этапов 23-30 сначала смотреть на соответствующий ADR.
- Если старый ADR содержит подробные примеры будущего кода, они считаются иллюстрациями, а не обязательным способом реализации.
- Roadmap этапов 20-31 является актуальной картой дальнейших работ.

## Сжатая карта решений

| ADR | Статус | Краткое действующее решение |
| --- | --- | --- |
| `0001-use-poetry` | принято | Зависимости ведутся через Poetry и `pyproject.toml`. |
| `0002-session-cart` | принято | Гость хранит корзину в session, авторизованный пользователь - в DB; при входе session-cart объединяется с DB-cart. |
| `0003-jwt-for-api` | принято | Web использует session auth, внешнее API использует JWT access/refresh. |
| `0004-order-transaction` | принято | Создание заказа выполняется в транзакции с повторной проверкой остатков. |
| `0005-domain-model` | принято | Домен разделён на `users`, `catalog`, `cart`, `orders`, `reviews`, `payments`, `api`. |
| `0006-soft-delete` | принято | Soft delete ограничен каталогом: `Category` и `Product`. |
| `0007-username-user-login` | принято | Основной логин - `username`; email остаётся контактным полем. |
| `0008-payment-order` | принято, требует пересмотра на этапе 25 | Один заказ может иметь несколько платежей; после `C035` checkout должен использовать payment emulator. |
| `0009-img-source` | принято, уточнено ADR `0031` | Runtime-источник изображений товара - `ProductImage`; `src/prepare` не используется напрямую. |
| `0010-button` | принято | Кнопка покупки должна быть связана с реальным cart endpoint и не имитировать несуществующее действие. |
| `0011-reviews-rating` | принято | Публичный рейтинг считается только по опубликованным отзывам. |
| `0012-rule-product` | принято | Похожие товары берутся из активной категории и исключают текущий товар. |
| `0013-cart-web-routes` | принято | Web-корзина имеет явные POST-маршруты для add/update/remove/clear. |
| `0014-cart-service-layer` | принято | Бизнес-логика корзины находится в service layer, views остаются HTTP-слоем. |
| `0015-cart-merge-timing` | принято | Merge session-cart в DB-cart выполняется после успешного login-flow. |
| `0016-cart-quantity-policy` | принято | Количество ограничено остатком и системным лимитом позиции. |
| `0017-session-cart-invalid-products` | принято | Недоступные товары показываются с предупреждением и блокируют checkout. |
| `0021-review-eligible-order-status` | принято | Отзыв разрешён после заказа с товаром в подтверждённом статусе. |
| `0022-review-web-create-contract` | принято | Web-создание отзыва идёт через `reviews` app и создаёт pending review. |
| `0023-api-architecture-boundary` | принято, сжато | REST API централизован в `apps/api`, доменная логика переиспользует service layer. |
| `0024-product-api-contract` | принято, уточняется `C036` | Основной Product API использует slug; этап 27 добавит id compatibility routes. |
| `0025-api-cart-contract` | принято, уточняется `C036` | API-корзина работает с DB-cart авторизованного JWT-пользователя; этап 27 добавит совместимый `/api/cart/`. |
| `0026-api-order-create-contract` | принято, требует пересмотра на этапе 25 | API checkout создаёт заказ из текущей корзины; payment outcome должен учитывать emulator. |
| `0027-api-registration-jwt` | принято, уточняется `C036` | API-регистрация создаёт пользователя и возвращает JWT pair; этап 27 добавит login alias. |
| `0028-review-api-contract` | принято, уточняется `C036` | Review API связан с product slug и service layer; id compatibility решается отдельно. |
| `0029-api-error-permissions-contract` | принято | API ошибки приводятся к единому JSON `{code, detail, fields}`; чужие заказы скрываются через 404. |
| `0030-seed-data-policy` | принято, уточнено ADR `0036` | Seed идемпотентен, безопасен и не зависит от `src/prepare`; demo-data русифицируется при сохранении ASCII technical keys. |
| `0031-myshop-brand-and-runtime-assets` | принято | Hop & Barley остаётся reference-концептом; runtime UI, branding и tracked assets принадлежат `MyShop` и не зависят от `src/prepare`. |
| `0032-admin-ui-and-dashboard` | принято | Улучшаем стандартный Django Admin через branding, шаблоны, стили и staff dashboard без замены базовой admin-механики. |
| `0033-payment-emulator` | принято | Checkout использует `apps.payment_emulator` с весами `succeeded=7`, `failed=1`, `cancelled=1`, `pending=1`; `payments` остаётся владельцем `Payment`. |
| `0034-api-compatibility-routes` | принято | Slug routes сохраняются; id/login/cart compatibility routes добавляются поверх существующего API и переиспользуют service/error contracts. |
| `0035-production-runtime` | принято | Dev stand остаётся на `runserver`, production runtime использует Gunicorn, Nginx, HTTPS, volumes, `collectstatic` и env-based secure settings. |
| `0036-russian-demo-data` | принято | Пользовательские demo/template данные русифицируются, а `slug`, `SKU`, `username` и provider ids остаются ASCII. |
| `0037-analytics-service-layer` | принято | Admin dashboard и GraphQL analytics используют общий read/service layer для одинаковых метрик и единых тестов агрегатов. |

## Будущие ADR

На текущий момент отдельные будущие ADR не запланированы. Новые ADR нужны, если будущая реализация меняет границы приложений, публичные API contracts, security model, production runtime или правила работы с данными.

## Требования к новым ADR

- Длина по умолчанию: до 120 строк.
- Обязательные разделы: статус, контекст, решение, последствия, связанные конфликты.
- Не вставлять большие примеры кода; достаточно контрактов, инвариантов и критериев приемки.
- Если нужен пример API payload или SQL/ORM-подход, вынести его в профильную документацию после реализации.
