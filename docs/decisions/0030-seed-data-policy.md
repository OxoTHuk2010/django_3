# ADR 0030: Политика seed-данных и использование `src/prepare/`

## Статус

Принято.

## Актуальная сжатая версия

- `seed_demo_data` должна быть идемпотентной и безопасной.
- `--reset` допускается только с `--yes` и только в local/demo окружении.
- `src/prepare` не является runtime-зависимостью seed-команды.
- После появления конфликта `C038` demo-data нужно расширить и привести к русскоязычному формату.
- Технические ключи остаются ASCII: `slug`, `SKU`, `username`, `provider_payment_id`.
- После этапа 22 demo-data должна поддерживать проверку витрины, admin analytics and GraphQL analytics.
- Подробные примеры ниже являются историческим контекстом и должны быть пересмотрены при реализации этапа 22.

## Контекст

В рамках этапа 18 планируется добавить management command для наполнения проекта демонстрационными данными:

```text
python manage.py seed_demo_data
```

На текущий момент команды seed ещё нет.

В проекте существует каталог:

```text
src/prepare/
```

Он сохранён как источник будущих UI-материалов, тестовых данных, идей для демо-витрины и вспомогательных ассетов. При этом `src/prepare/` находится в `.gitignore` и не должен становиться runtime-зависимостью проекта.

Ранее по ADR 0009 было принято, что `ProductImage` является единственным runtime-источником изображений товара, а `src/prepare/` не используется напрямую в рабочей реализации.

Конфликт C031 связан с тем, как должна работать seed-команда и можно ли использовать материалы из `src/prepare/` при создании demo-данных.

Нужно определить:

```text
- является ли seed-команда идемпотентной;
- нужен ли destructive-флаг --reset;
- можно ли использовать src/prepare/;
- какие demo-пользователи создаются;
- какие категории, товары, заказы, оплаты и отзывы создаются;
- как не повредить реальные данные в локальной или демонстрационной БД.
```

## Решение

Принимаем следующее решение:

```text
seed_demo_data по умолчанию должна быть идемпотентной и безопасной.
```

Команда:

```text
python manage.py seed_demo_data
```

создаёт или обновляет только заранее известные demo-данные и не должна бесконтрольно плодить дубликаты при повторном запуске.

Destructive-режим разрешён только через явный флаг:

```text
python manage.py seed_demo_data --reset
```

Флаг `--reset` должен быть доступен только для локального/demo окружения и иметь stop-условия, защищающие от случайного удаления данных в production.

`src/prepare/` может использоваться только как источник исходных материалов при подготовке seed-данных, но не как обязательная runtime-зависимость команды.

Итоговое правило:

```text
src/prepare/ не является частью runtime.
seed_demo_data не должна падать только потому, что src/prepare/ отсутствует.
```

## Политика идемпотентности

Базовый запуск:

```text
python manage.py seed_demo_data
```

должен быть идемпотентным.

Это означает:

```text
- повторный запуск не создаёт дубликаты категорий;
- повторный запуск не создаёт дубликаты товаров;
- повторный запуск не создаёт дубликаты demo-пользователей;
- повторный запуск не создаёт дубликаты seed-заказов;
- повторный запуск не создаёт дубликаты seed-отзывов;
- существующие demo-записи обновляются только в пределах seed-owned данных.
```

Для идемпотентности необходимо использовать стабильные ключи.

Рекомендуемые стабильные ключи:

```text
Category.slug
Product.slug
Product.sku
User.username
Order.demo_key, если такое поле появится
Payment.external_id или demo_key, если такое поле появится
Review user + product
```

Если специальных `demo_key` полей в моделях нет, seed-команда должна использовать существующие уникальные поля и явно ограничивать работу только demo-записями.

## Политика `--reset`

Флаг:

```text
--reset
```

разрешает удалить ранее созданные demo-данные и создать их заново.

`--reset` не должен быть обычным режимом работы.

Перед destructive-операциями команда должна проверить окружение.

Минимальные stop-условия:

```text
1. Запрещено выполнять --reset при DEBUG=False.
2. Запрещено выполнять --reset, если ENVIRONMENT=production.
3. Запрещено выполнять --reset, если DJANGO_SETTINGS_MODULE указывает на production-настройки.
4. Желательно требовать дополнительный флаг подтверждения --yes.
```

Рекомендуемый destructive запуск:

```text
python manage.py seed_demo_data --reset --yes
```

Если `--reset` передан без `--yes`, команда должна остановиться с понятным сообщением.

Пример:

```text
Refusing to reset demo data without --yes.
```

Если окружение похоже на production, команда должна завершиться ошибкой.

Пример:

```text
Refusing to reset demo data outside local/demo environment.
```

## Граница удаления при `--reset`

`--reset` должен удалять только seed-owned данные.

Недопустимо:

```text
- удалять все товары без разбора;
- удалять все категории без разбора;
- удалять всех пользователей;
- удалять все заказы;
- очищать всю БД;
- выполнять flush;
- выполнять migrate reset;
- удалять пользовательские записи, не созданные seed-командой.
```

Допустимо:

```text
- удалить demo-пользователей по известным username;
- удалить demo-категории по известным slug;
- удалить demo-товары по известным slug или sku;
- удалить demo-заказы, связанные с demo-пользователями;
- удалить demo-отзывы, связанные с demo-пользователями и demo-товарами;
- удалить demo-платежи, связанные с demo-заказами.
```

Если в проекте появится поле:

```text
is_demo
```

или отдельная таблица учёта seed-данных, `--reset` может использовать его как основной маркер владения.

На текущем этапе достаточно стабильных известных ключей.

## Использование `src/prepare/`

`src/prepare/` не является runtime-зависимостью приложения.

Seed-команда не должна импортировать или читать `src/prepare/` как обязательный источник.

Допустимые варианты использования:

```text
1. Разработчик вручную переносит выбранные ассеты из src/prepare/ в нормальный каталог seed-ресурсов.
2. Seed-команда имеет необязательный флаг --with-prepare-assets.
3. При отсутствии src/prepare/ команда продолжает работу без изображений или использует встроенные neutral/demo assets.
```

Недопустимое поведение:

```text
- шаблоны обращаются к src/prepare/;
- views обращаются к src/prepare/;
- ProductImage хранит runtime-путь на src/prepare/;
- seed_demo_data падает, если src/prepare/ отсутствует;
- production или test-запуск зависит от src/prepare/.
```

Для изображений demo-товаров рекомендуется создать отдельный контролируемый каталог, который может быть включён в репозиторий:

```text
src/static/demo/
```

или:

```text
src/seed_assets/
```

Если такие ассеты тяжёлые или не должны храниться в Git, seed-команда должна уметь создавать товары без изображений.

## Источник demo-данных

Demo-данные должны быть описаны явно в коде seed-команды или в контролируемых seed fixtures.

Допустимые варианты:

```text
- Python-структуры внутри management command;
- отдельные JSON/YAML fixtures в репозитории;
- небольшие статические demo-assets в контролируемом каталоге;
- factory/helper-функции для создания demo-объектов.
```

Для MVP предпочтительно:

```text
Python-структуры внутри management command.
```

Причина:

```text
- проще контролировать идемпотентность;
- проще использовать update_or_create;
- проще связывать категории, товары, заказы, оплаты и отзывы;
- проще не зависеть от внешних файлов.
```

## Demo-пользователи

Seed-команда может создавать минимальный набор demo-аккаунтов.

Рекомендуемый состав:

```text
demo_customer
demo_customer_2
demo_staff
```

Минимальный набор:

```text
demo_customer
```

Для demo-пользователей должны использоваться понятные, но небезопасные только для local/demo окружения пароли.

Пример:

```text
username: demo_customer
password: demo12345
email: demo_customer@example.com
```

```text
username: demo_staff
password: demo12345
email: demo_staff@example.com
is_staff: True
```

Важно:

```text
Demo-пароли запрещено использовать в production.
```

Если команда обнаруживает production-like окружение, она не должна создавать demo-пользователей.

## Demo-категории

Seed-команда должна создавать небольшой набор активных публичных категорий.

Пример:

```text
electronics
books
home
clothes
```

Для проверки edge cases можно создать отдельные скрытые категории, но только если они нужны тестам или демонстрации.

Например:

```text
hidden-demo-category
```

Однако публичная витрина должна показывать только активные неудалённые категории.

## Demo-товары

Seed-команда должна создавать набор товаров, достаточный для демонстрации:

```text
- списка товаров;
- детальной страницы;
- поиска;
- фильтра категории;
- фильтра цены;
- сортировки;
- пагинации;
- состояния "В наличии";
- состояния "Нет в наличии";
- old_price;
- main image, если demo-assets доступны;
- нескольких изображений товара, если demo-assets доступны.
```

Рекомендуемый минимум:

```text
12-20 товаров
```

Причина: этого достаточно для проверки пагинации и фильтров без избыточного шума.

Для товаров должны использоваться стабильные:

```text
slug
sku
```

Пример товара:

```text
slug: demo-smartphone-basic
sku: DEMO-SMARTPHONE-BASIC
name: Смартфон Demo Basic
stock_quantity: 10
is_active: True
is_deleted: False
```

## Demo-изображения

Изображения должны создаваться через модель:

```text
ProductImage
```

Это согласуется с ADR 0009.

Правило:

```text
ProductImage остаётся единственным runtime-источником изображений товара.
```

Если demo-assets доступны, команда может создать `ProductImage`.

Если demo-assets недоступны, команда должна создать товары без изображений и не падать.

На этапе MVP placeholder не обязателен.

## Demo-заказы

Seed-команда может создавать demo-заказы для проверки личного кабинета, отзывов, API и статусов заказа.

Рекомендуемый набор статусов:

```text
paid
processing
shipped
completed
cancelled
```

Статус:

```text
new
```

можно создать отдельно, если он нужен для демонстрации незавершённого заказа.

Минимально полезный набор:

```text
- один paid заказ;
- один completed заказ;
- один cancelled заказ.
```

Заказы должны быть связаны с demo-пользователями и demo-товарами через `OrderItem`.

Если checkout service уже существует и умеет атомарно создавать заказ из корзины, seed-команда может использовать service-layer.

Если это усложняет seed, допустимо создавать demo-заказы напрямую, но только при условии соблюдения структуры моделей и очевидной маркировки demo-данных.

Предпочтительно:

```text
Использовать domain services, если они не требуют реального HTTP request.
```

## Demo-платежи

Для demo-заказов seed-команда может создавать локальные demo-платежи через `provider=payment_emulator`.

Рекомендуемый набор:

```text
- paid payment для paid/completed заказов;
- failed или cancelled payment, если такие статусы есть в модели;
- refund не создавать до появления явной refund-логики.
```

Если в текущей модели Payment уже есть provider/status, использовать:

```text
provider = payment_emulator
status = succeeded
```

или фактические значения enum из модели.

Платежи должны быть связаны только с demo-заказами.

## Demo-отзывы

Seed-команда может создавать demo-отзывы для товаров.

Рекомендуемый набор:

```text
- published отзывы для отображения рейтинга;
- pending отзыв для проверки модерации;
- rejected/hidden отзыв, если такие статусы есть и нужны для проверки фильтрации.
```

Публичная витрина и Product API должны показывать только:

```text
published
```

Отзывы должны соблюдать бизнес-правило:

```text
Оставить отзыв может только пользователь с подтверждённой покупкой.
```

Поэтому demo-отзыв должен создаваться только для demo-пользователя и demo-товара, который есть в его demo-заказе со статусом, дающим право на отзыв.

Это согласуется с ADR 0021.

`Review.is_verified_purchase` для таких отзывов должен быть:

```text
True
```

## Данные, допустимые для Docker PostgreSQL перед демонстрацией

Для локальной Docker PostgreSQL перед демонстрацией допустимо создавать:

```text
- demo-пользователей;
- demo-категории;
- demo-товары;
- demo-изображения, если assets доступны;
- demo-заказы;
- demo-платежи;
- demo-отзывы;
- минимальные данные для проверки web и API.
```

Недопустимо:

```text
- создавать реальные персональные данные;
- использовать реальные email клиентов;
- использовать production-like пароли;
- загружать конфиденциальные изображения;
- смешивать demo-данные с реальными данными без маркировки;
- выполнять destructive reset в production-like окружении.
```

## Поведение команды

Базовое поведение:

```text
python manage.py seed_demo_data
```

Должно:

```text
- проверить окружение;
- создать или обновить demo-пользователей;
- создать или обновить demo-категории;
- создать или обновить demo-товары;
- создать ProductImage, если demo-assets доступны;
- создать demo-заказы;
- создать demo-платежи;
- создать demo-отзывы;
- вывести краткую статистику созданных/обновлённых объектов.
```

Пример вывода:

```text
Demo data seeding completed.
Users: created=1 updated=2
Categories: created=4 updated=0
Products: created=16 updated=0
Orders: created=3 updated=0
Payments: created=3 updated=0
Reviews: created=8 updated=0
```

## Последствия

Плюсы решения:

```text
- seed-команда безопасна при повторном запуске;
- локальная разработка и демонстрации получают предсказуемые данные;
- --reset явно отделён от обычного режима;
- production защищён от случайного destructive seed;
- src/prepare/ не становится runtime-зависимостью;
- demo-данные покрывают реальные сценарии каталога, корзины, заказов, платежей и отзывов;
- seed-данные помогают проверять web и API без ручного наполнения.
```

Минусы решения:

```text
- seed-команда сложнее, чем простая загрузка fixtures;
- нужно поддерживать стабильные ключи demo-данных;
- --reset требует аккуратной реализации;
- demo-данные могут устаревать при изменении моделей;
- при отсутствии demo-assets товары могут быть без изображений;
- нужно следить, чтобы demo-пользователи и пароли не попали в production.
```

## Связанные документы / файлы / настройки

```text
- docs/roadmap.md
- docs/business-rules.md
- docs/decisions/0009-img-source.md
- docs/decisions/0021-review-eligible-order-status.md
- docs/conflicts.md
- docs/decisions/0030-seed-data-policy.md
- apps/catalog/models.py
- apps/orders/models.py
- apps/payments/models.py
- apps/reviews/models.py
- apps/users/models.py
- apps/catalog/management/commands/seed_demo_data.py
- src/prepare/
- src/static/demo/
- media/
```

## Инварианты для реализации

```text
1. seed_demo_data по умолчанию идемпотентна.
2. Повторный запуск seed_demo_data не создаёт дубликаты demo-данных.
3. --reset является явным destructive-режимом.
4. --reset запрещён при DEBUG=False.
5. --reset запрещён в production-like окружении.
6. --reset желательно требует дополнительный флаг --yes.
7. --reset удаляет только seed-owned данные.
8. seed_demo_data не должна выполнять flush всей БД.
9. src/prepare/ не является runtime-зависимостью.
10. Отсутствие src/prepare/ не должно ломать seed.
11. ProductImage является источником demo-изображений товара.
12. Demo-пользователи имеют явно demo-username и demo-email.
13. Demo-пароли разрешены только для local/demo окружения.
14. Demo-заказы создаются только для demo-пользователей.
15. Demo-платежи создаются только для demo-заказов.
16. Demo-отзывы должны соблюдать правило подтверждённой покупки.
17. Публичные demo-отзывы должны иметь status=published.
18. Pending/rejected/hidden отзывы не должны отображаться в публичной витрине.
```

## Пример структуры management command

```python
# apps/catalog/management/commands/seed_demo_data.py

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or reset demo data for local development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before seeding.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm destructive reset.",
        )
        parser.add_argument(
            "--with-prepare-assets",
            action="store_true",
            help="Try to use optional assets from src/prepare/ if present.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        confirmed = options["yes"]

        if reset:
            self._validate_reset_allowed(confirmed=confirmed)
            self._reset_demo_data()

        self._seed_users()
        self._seed_categories()
        self._seed_products(
            with_prepare_assets=options["with_prepare_assets"],
        )
        self._seed_orders()
        self._seed_payments()
        self._seed_reviews()

        self.stdout.write(
            self.style.SUCCESS("Demo data seeding completed.")
        )

    def _validate_reset_allowed(self, *, confirmed):
        if not settings.DEBUG:
            raise CommandError(
                "Refusing to reset demo data when DEBUG=False."
            )

        environment = getattr(settings, "ENVIRONMENT", "local")

        if environment in {"production", "prod"}:
            raise CommandError(
                "Refusing to reset demo data in production environment."
            )

        if not confirmed:
            raise CommandError(
                "Refusing to reset demo data without --yes."
            )
```

## Пример стабильных demo-ключей

```python
DEMO_USERS = [
    {
        "username": "demo_customer",
        "email": "demo_customer@example.com",
        "password": "demo12345",
    },
    {
        "username": "demo_customer_2",
        "email": "demo_customer_2@example.com",
        "password": "demo12345",
    },
]

DEMO_CATEGORIES = [
    {
        "slug": "electronics",
        "name": "Электроника",
    },
    {
        "slug": "books",
        "name": "Книги",
    },
]

DEMO_PRODUCTS = [
    {
        "slug": "demo-smartphone-basic",
        "sku": "DEMO-SMARTPHONE-BASIC",
        "name": "Смартфон Demo Basic",
        "category_slug": "electronics",
        "price": "19990.00",
        "old_price": "24990.00",
        "stock_quantity": 10,
    },
]
```

## Пример безопасного создания

```python
category, _ = Category.objects.update_or_create(
    slug="electronics",
    defaults={
        "name": "Электроника",
        "is_active": True,
        "is_deleted": False,
    },
)

product, _ = Product.objects.update_or_create(
    sku="DEMO-SMARTPHONE-BASIC",
    defaults={
        "slug": "demo-smartphone-basic",
        "name": "Смартфон Demo Basic",
        "category": category,
        "price": "19990.00",
        "old_price": "24990.00",
        "stock_quantity": 10,
        "is_active": True,
        "is_deleted": False,
    },
)
```

## Пример тестовых ожиданий

```text
1. Первый запуск seed_demo_data создаёт demo-данные.
2. Повторный запуск seed_demo_data не создаёт дубликаты.
3. Повторный запуск seed_demo_data обновляет demo-записи по стабильным ключам.
4. seed_demo_data --reset без --yes завершается ошибкой.
5. seed_demo_data --reset при DEBUG=False завершается ошибкой.
6. seed_demo_data --reset удаляет только demo-пользователей и связанные demo-данные.
7. seed_demo_data не выполняет flush БД.
8. Отсутствие src/prepare/ не ломает seed.
9. --with-prepare-assets не обязателен для успешного seed.
10. Demo-товары создаются с уникальными slug и sku.
11. Demo-отзывы создаются только для купленных demo-товаров.
12. Demo-отзывы published отображаются на странице товара.
13. Demo-отзывы pending не отображаются публично.
14. Demo-заказы связаны с demo-пользователями.
15. Demo-платежи связаны только с demo-заказами.
```

## Примечание по будущему развитию

Если seed-данные станут крупнее, можно перейти к более формальному механизму учёта seed-owned записей.

Возможные варианты:

```text
- поле is_demo в основных моделях;
- отдельная таблица SeedRecord;
- namespace demo-slug/demo-sku;
- fixtures + post-processing command;
- фабрики через model-bakery/factory_boy только для dev/test.
```

Такое изменение должно быть оформлено отдельным ADR, если оно меняет правила удаления, обновления или источники demo-данных.

На этапе 18 действует правило:

```text
seed_demo_data безопасна, идемпотентна, не зависит от src/prepare/
и не выполняет destructive-действия без явного локального подтверждения.
```
