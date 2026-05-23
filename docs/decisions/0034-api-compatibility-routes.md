# ADR 0034: Compatibility routes для REST API

## Статус

Принято.

## Контекст

Текущий Product API использует slug routes, например `GET /api/products/<slug>/` и `GET/POST /api/products/<slug>/reviews/`.

В исходной таблице API из ТЗ встречаются routes с `<id>`. Если заменить slug routes на id routes, будут сломаны существующие endpoints, тесты и документация. Если оставить только slug routes, формальное соответствие ТЗ останется неполным.

## Решение

Не ломать текущий API. Добавить compatibility routes поверх существующих slug routes.

Минимальный набор этапа 27:

- сохранить `GET /api/products/<slug>/`;
- добавить `GET /api/products/<int:id>/`;
- добавить `POST /api/users/login/` как alias JWT token obtain;
- добавить совместимые `GET/POST/PATCH/DELETE /api/cart/`;
- добавить id-compatible review endpoints только если это потребуется итоговым API checklist.

Одинаковые сценарии должны переиспользовать один service/selectors layer и возвращать тот же error contract из ADR 0029.

## Последствия

Плюсы:

- текущие клиенты и тесты со slug routes продолжают работать;
- API лучше соответствует таблице ТЗ;
- business rules остаются в одном service layer.

Минусы:

- увеличивается количество публичных routes;
- OpenAPI и `docs/api.md` нужно явно описывать alias/compatibility поведение;
- нужно тестировать, что slug и id routes возвращают согласованные данные.

## Инварианты

- Slug routes не удаляются.
- Id routes являются compatibility layer, а не отдельной бизнес-логикой.
- Ошибки compatibility routes используют формат `{code, detail, fields}`.
- Чужие приватные ресурсы продолжают скрываться через правила ADR 0029.

## Связанные конфликты

- `C036` — REST API slug routes vs URL table from ТЗ.
