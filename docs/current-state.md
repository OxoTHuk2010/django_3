# Текущее состояние проекта

Дата оценки: 2026-05-24.

Документ фиксирует фактический baseline перед следующими этапами. Ручные проверки текущего web-состояния уже выполнены отдельно; ниже зафиксированы инженерная оценка, автоматические проверки и ближайшие реализуемые направления.

## Итоговая оценка

Проект находится в состоянии функционального MVP интернет-магазина:

- доменная модель разделена на `users`, `catalog`, `cart`, `orders`, `reviews`, `payments`, `api`;
- публичный web-интерфейс покрывает главную, каталог, карточку товара, корзину, checkout, регистрацию, вход, профиль, историю и детали заказов;
- корзина реализована для гостя через session и для авторизованного пользователя через DB-cart;
- checkout создаёт заказ атомарно через service layer и списывает остатки;
- отзывы создаются через отдельное приложение `reviews` и проверяют право пользователя по подтверждённой покупке;
- REST API вынесен в `apps/api`, использует JWT, единый слой serializers/views и покрывает продукты, корзину, заказы, регистрацию и отзывы;
- Swagger/OpenAPI подключён через drf-spectacular;
- demo-data создаётся management command `seed_demo_data`, команда идемпотентна и защищает destructive reset;
- современная админка реализована как кастомизация стандартного Django Admin: branding, staff dashboard, отдельная admin-статика, верхняя навигация, бейджи статусов товаров и быстрые ссылки в `ProductAdmin`;
- админская аналитика реализована на `/admin/` через общий read/service слой `apps.common.analytics`: метрики, периодный фильтр, низкие остатки, топ товаров и отзывы на модерации;
- UI-шаблоны и runtime-статика перенесены в `src/templates` и `src/static/shop`, при этом `src/prepare` остаётся reference/source, а не runtime-зависимостью;
- reference UI перенесён в рабочие Django-шаблоны с русской локализацией и текущим брендом `MyShop`: header/footer, hero/banner, sidebar filters, product grid, карточки, auth forms, корзина и checkout;
- runtime JS подключён из `src/static/shop/js/main.js` как progressive enhancement для аккордеонов, фильтров и quantity controls; симуляция login/cart из reference-прототипа не переносилась, потому что проект использует реальные Django-сессии и POST-формы;
- reference product images перенесены в `src/static/shop/img/products`, а `seed_demo_data` создаёт штатные `ProductImage` через копирование в `MEDIA_ROOT/demo/products`;
- этапы 20, 21, 22, 23 и 24 закрыты: baseline зафиксирован, бренд runtime UI — `MyShop`, пользовательские UI-тексты и demo-data русскоязычные, CSS/JS/images находятся в tracked static, админка улучшена без замены стандартного Django Admin, аналитика вынесена в общий service layer.

Проект ещё не является production-ready поставкой: нет полноценного production runtime с Gunicorn/Nginx/HTTPS, нет CI, нет отдельного payment emulator.

## Проверенный baseline

Автоматические проверки на 2026-05-24:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py collectstatic --dry-run --noinput --clear
.\.venv\Scripts\python.exe -m ruff check . --no-cache
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Результат:

- `manage.py check` проходит без замечаний;
- `makemigrations --check --dry-run` сообщает `No changes detected`;
- `collectstatic --dry-run --noinput --clear` видит `src/static/shop/css/main.css`, `src/static/shop/js/main.js`, `src/static/admin_shop/css/admin.css` и перенесённые изображения, проходит;
- `ruff check` проходит;
- `pytest` проходит: `166 passed`, coverage `90%`;
- единственное предупреждение тестового прогона: `InsecureKeyLengthWarning` из SimpleJWT из-за короткого dev `SECRET_KEY`; это не блокирует локальную разработку, но production secret должен быть длинным и внешним.

Ручные проверки предыдущего UI были выполнены до переноса reference-дизайна. После текущих изменений выполнена автоматическая и HTTP smoke-проверка; отдельный визуальный ручной цикл по браузеру нужен перед фиксацией финального UI baseline.

## Что можно реализовывать уже сейчас

Эти этапы можно брать в работу без дополнительных архитектурных блокеров:

1. UX-полировка web-флоу.
   Можно улучшать сообщения после действий, пустые состояния корзины/заказов/отзывов, визуальные состояния ошибок и доступность форм без изменения доменной архитектуры.

2. Финальная локальная/Docker-проверка MVP.
   Можно провести новый clean-run через Docker Compose, seed, web-flow, Swagger и JWT, затем закрыть этап 19 как актуальный baseline.

3. Небольшие улучшения тестов.
   Можно добавлять focused tests на шаблоны, messages, manual-check regressions и seed-data scenarios без пересмотра архитектуры.

## Что лучше подготовить ADR перед реализацией

Следующие направления затрагивают архитектурные решения и должны начинаться с компактного ADR или обновления существующего решения:

- отдельный payment emulator вместо текущего mock-success checkout;
- email-уведомления;
- REST API compatibility routes;
- GraphQL аналитика;
- CI;
- production runtime: Gunicorn/Nginx/HTTPS/static/media handling.

Причина: эти работы меняют публичные контракты, инфраструктуру или границы ответственности приложений. Их лучше начинать после закрытия ближайших UI/demo-data долгов.

## Остаточные риски

- Runtime-статика вынесена в `src/static/shop`, но production static serving ещё зависит от этапа 30.
- Media-файлы demo-товаров создаются seed-командой в `MEDIA_ROOT/demo/products`; production media serving ещё зависит от этапа 30.
- Production settings минимальны; реальные `SECRET_KEY`, `ALLOWED_HOSTS`, secure cookies, HTTPS и static serving ещё требуют отдельной настройки.
- Payment flow пока mock-success внутри checkout; для более реалистичного поведения нужен отдельный payment emulator.
- API покрыт тестами, но compatibility routes и versioning ещё не реализованы.

## Рекомендуемый порядок ближайших работ

1. Повторить полный ручной и автоматический baseline после UI/demo-data переноса.
2. Закрыть этап 25: payment emulator.
3. После этого выбрать один крупный архитектурный трек: email, compatibility API, GraphQL, CI или production runtime.
