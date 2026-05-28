# Roadmap

Roadmap отражает фактические этапы реализации и ближайшие действия. Подробные правила находятся в профильных документах: `architecture.md`, `business-rules.md`, `database.md`, `api.md`, `testing.md`.

## Легенда

- `[x]` выполнено
- `[ ]` не выполнено
- `[!]` требует отдельного решения

## Baseline

Дата последней проверки: 2026-05-24.

- [x] `python manage.py check` проходит.
- [x] `python manage.py makemigrations --check --dry-run` проходит.
- [x] `ruff check . --no-cache` проходит.
- [x] `mypy src` проходит.
- [x] `pytest -q -p no:cacheprovider` проходит: `190 passed`, coverage `89%`.
- [x] Dev Docker Compose валиден.
- [x] Production Docker Compose валиден.
- [x] Dev и production Docker images собираются.
- [x] `.env` и `.env.example` не попадают в Docker images.

## Выполненные этапы

- [x] 0. Цель проекта и порядок реализации.
- [x] 1. Инициализация Django/Poetry проекта.
- [x] 2. Settings, `.env.example`, DRF, JWT, Swagger, custom user.
- [x] 3. Docker Compose и PostgreSQL.
- [x] 4. Базовые модели, миграции и model tests.
- [x] 5. Django Admin, inline forms и admin actions.
- [x] 6. Каталог товаров: список, поиск, фильтры, сортировка, пагинация.
- [x] 7. Детальная страница товара: изображения, остатки, рейтинг, отзывы, похожие товары.
- [x] 8. Корзина: session-cart, DB-cart, merge, операции add/update/remove/clear.
- [x] 9. Checkout и заказы: транзакция, snapshot данных, списание остатков.
- [x] 10. Пользователи и личный кабинет.
- [x] 11. Отзывы: право оставить отзыв, модерация, тесты.
- [x] 12. REST API: products, cart, orders, users, reviews.
- [x] 13. Swagger/OpenAPI.
- [x] 14. Документация.
- [x] 15. Качество кода: Ruff, mypy, pytest config.
- [x] 16. Тестовая стратегия и покрытие бизнес-правил.
- [x] 17. UX-полировка web-интерфейса.
- [x] 18. Seed demo-data.
- [x] 19. Финальная проверка MVP-сценариев.
- [x] 20. Baseline текущего состояния.
- [x] 21. Русскоязычный runtime UI и demo-data.
- [x] 22. Подключение runtime assets для web-интерфейса.
- [x] 23. Улучшение Django Admin.
- [x] 24. Админская аналитика через service layer.
- [x] 25. Payment emulator.
- [x] 26. Email-уведомления после checkout.
- [x] 27. API compatibility routes.
- [x] 28. GraphQL исключён из текущего scope.
- [x] 29. GitHub Actions CI.
- [x] 30. Production runtime.
- [x] 31. Production deploy workflow для self-hosted runner.

## Финальная стабилизация

- [ ] 32. Clean-run по README на чистой базе.
- [ ] Проверить ручной web-smoke после `seed_demo_data`.
- [ ] Проверить Swagger и основные API-запросы с JWT.
- [ ] Проверить GitHub Actions после push/PR.
- [ ] Зафиксировать финальные known limitations.

## Definition of Done для финальной сдачи

- [ ] Проект запускается через Docker Compose по README.
- [ ] Миграции применяются на чистой БД.
- [ ] Seed demo-data создаёт демонстрационный набор без секретов в репозитории и запускается в production deploy только через явные runtime-флаги.
- [ ] Главная, каталог, карточка товара, корзина, checkout, личный кабинет и admin открываются вручную.
- [ ] Swagger открывается, JWT выдаётся, основные API endpoints работают.
- [ ] `pytest`, `ruff`, `mypy`, `check`, `makemigrations --check --dry-run` проходят.
- [ ] Документация соответствует текущему коду и не содержит рабочие заметки.

## Правила обновления roadmap

- Roadmap обновляется после закрытия этапа или изменения scope.
- Подробные технические правила не дублируются в roadmap.
- Архитектурные изменения сначала фиксируются в ADR, затем отражаются здесь одной строкой.
