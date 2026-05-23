# ADR 0031: Бренд MyShop и runtime-ассеты

## Статус

Принято.

## Контекст

Этап 21 переносит reference UI из `src/prepare/` в рабочие Django-шаблоны и статику.

В `src/prepare/` исходный дизайн был подготовлен как Hop & Barley template. При прямом переносе бренд, тексты, title, навигация и admin branding расходились бы с проектом `MyShop`.

Отдельный риск: `src/prepare/` является reference/source каталогом, а не частью runtime-структуры. Runtime-код, шаблоны, `collectstatic`, Docker build и production deployment не должны зависеть от него.

## Решение

Использовать Hop & Barley только как исторический дизайн-концепт.

Во всех runtime-шаблонах, title, navigation, alt-текстах, admin branding, README и пользовательских текстах использовать бренд `MyShop`.

Runtime-ассеты и шаблоны должны жить в tracked runtime-директориях:

- публичная статика: `src/static/shop/`;
- будущая admin-статика: `src/static/admin_shop/`;
- Django-шаблоны: доменные template-директории приложения.

`src/prepare/` не является runtime-зависимостью. Runtime-код не импортирует, не читает и не линкует файлы из `src/prepare/`.

## Последствия

Плюсы:

- проект выглядит как цельная сдача `MyShop`, а не как неадаптированный внешний шаблон;
- clean clone, `collectstatic`, Docker build и production deployment не требуют `src/prepare/`;
- reference UI можно сохранять для истории и будущих дизайн-уточнений.

Минусы:

- перенос изменений из reference UI требует явной адаптации;
- нужно поддерживать соответствие runtime-шаблонов текущим Django URL, forms и service contracts.

## Инварианты

- Публичный UI не упоминает Hop & Barley.
- Runtime-шаблоны используют `{% static %}` для tracked ассетов.
- `src/prepare/` можно удалить из чистой копии без поломки runtime.
- Admin branding использует `MyShop`.

## Связанные конфликты

- `C032` — MyShop vs Hop & Barley template.
- `C033` — `src/prepare` как источник дизайна vs runtime-зависимость.
