# ADR 0037: Общий service layer для admin и GraphQL аналитики

## Статус

Принято.

## Контекст

Аналитика требуется в двух местах: staff-only admin dashboard и GraphQL endpoint `/graphql/`.

Источники данных одинаковые: `Order`, `OrderItem`, `Payment`, `Product`, `Review`, `User`. Если расчёты будут реализованы отдельно в admin views и GraphQL resolvers, метрики могут разойтись.

## Решение

Строить аналитику через общий read/service слой.

Общий слой отвечает за:

- расчёт выручки;
- количество заказов;
- средний чек;
- новых пользователей;
- оплаченные заказы;
- популярные товары;
- агрегаты, нужные admin dashboard и GraphQL analytics.

Admin dashboard и GraphQL resolvers не дублируют расчёты. Они отвечают только за доступ, представление и формат ответа.

## Последствия

Плюсы:

- admin и GraphQL показывают одинаковые метрики;
- основные тесты агрегатов пишутся один раз на service layer;
- будущие изменения формул не нужно синхронизировать в двух местах.

Минусы:

- перед UI/API реализацией нужно выделить явный analytics module;
- слой должен иметь понятные контракты фильтров, периодов и статусов;
- presentation tests всё равно нужны для admin и GraphQL.

## Инварианты

- Расчёты метрик не живут внутри templates, admin views или GraphQL resolvers.
- Staff-only access проверяется на уровне входных endpoint/view/resolver.
- Общий слой покрывается тестами агрегатов.
- Admin и GraphQL покрываются тестами доступа, формата ответа и smoke-сценариев.

## Связанные конфликты

- `C039` — admin analytics scope vs GraphQL analytics scope.
