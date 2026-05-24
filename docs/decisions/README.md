# ADR index

Индекс показывает действующие архитектурные решения. Обычные бизнес-правила, маршруты, UI-состояния и примеры запросов описываются в профильной документации, а не в ADR.

## Правила актуальности

- Ниже перечислены только ADR архитектурного уровня.
- Этап 28 исключён из текущего scope.
- Этапы 29-30 реализованы: CI и production runtime.
- Если старый вопрос больше не требует отдельного ADR, его итог переносится в `docs/business-rules.md`, `docs/api.md` или `docs/architecture.md`.

## Решения

| ADR | Статус | Решение |
| --- | --- | --- |
| `0001-use-poetry` | принято | Зависимости ведутся через Poetry и `pyproject.toml`. |
| `0002-session-cart` | принято | Гость хранит корзину в session, авторизованный пользователь — в DB; после входа выполняется merge. |
| `0003-jwt-for-api` | принято | Web использует session auth, API использует JWT access/refresh. |
| `0004-order-transaction` | принято | Заказ создаётся в транзакции с повторной проверкой остатков. |
| `0005-domain-model` | принято | Домен разделён на отдельные Django apps. |
| `0006-soft-delete` | принято | Soft delete ограничен каталогом: `Category` и `Product`. |
| `0007-username-user-login` | принято | Основной логин — `username`; email — контактное поле. |
| `0008-payment-order` | принято | Один заказ может иметь несколько платежей; успешный платёж не дублируется. |
| `0014-cart-service-layer` | принято | Бизнес-логика корзины находится в service layer. |
| `0023-api-architecture-boundary` | принято | REST API централизован в `apps/api`, бизнес-логика остаётся в доменных сервисах. |
| `0025-api-cart-contract` | принято | API-корзина требует JWT и работает с DB-cart. |
| `0026-api-order-create-contract` | принято | API checkout создаёт заказ из текущей DB-корзины пользователя. |
| `0027-api-registration-jwt` | принято | API-регистрация создаёт пользователя и возвращает JWT pair. |
| `0029-api-error-permissions-contract` | принято | Собственные API errors используют JSON `{code, detail, fields}`; чужие заказы скрываются через 404. |
| `0030-seed-data-policy` | принято | Seed идемпотентен, безопасен и не хранит пароли. |
| `0032-admin-ui-and-dashboard` | принято | Улучшается стандартный Django Admin без замены базовой механики. |
| `0033-payment-emulator` | принято | Checkout использует weighted payment emulator. |
| `0034-api-compatibility-routes` | принято | Compatibility routes добавлены без удаления основного API. |
| `0035-production-runtime` | принято | Dev и production runtime разделены. |
| `0037-analytics-service-layer` | принято | Админская аналитика считается через общий read/service layer; GraphQL исключён из текущего scope. |

## Требования к новым ADR

- ADR нужен только для архитектурных, security, deployment, persistence или публичных API-решений.
- Длина по умолчанию — до 120 строк.
- Обязательные разделы: статус, контекст, решение, последствия, связанные документы.
- Не хранить большие примеры кода, payload dumps, рабочие заметки и секреты.
