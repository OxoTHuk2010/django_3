# ADR 0035: Разделение dev stand и production runtime

## Статус

Принято.

## Контекст

Текущий Docker Compose запускает Django через `runserver` и PostgreSQL. Это удобно для локальной разработки, но не является production-ready runtime.

Этап 30 требует заложить закрытие сайта через Gunicorn, Nginx и HTTPS. При этом локальный dev stand должен оставаться простым и запускаться без обязательных сертификатов.

## Решение

Разделить dev и production сценарии.

Dev stand:

- сохраняет Django `runserver`;
- сохраняет PostgreSQL;
- не требует обязательный HTTPS;
- остаётся быстрым способом локального запуска.

Production runtime:

- использует Gunicorn как WSGI server;
- использует Nginx как reverse proxy;
- обслуживает static/media через volume and proxy rules;
- выполняет `collectstatic`;
- включает HTTP to HTTPS redirect;
- поддерживает Let's Encrypt/certbot или совместимый certbot script;
- получает secure settings через environment variables.

## Последствия

Плюсы:

- локальная разработка не усложняется production-сертификатами;
- production-путь получает отдельные настройки безопасности и web-server слой;
- инфраструктура становится понятнее для сдачи и будущего деплоя.

Минусы:

- появляются два сценария запуска, которые нужно документировать и проверять;
- production compose/profile требует отдельного обслуживания;
- HTTPS/certbot flow зависит от домена и внешней среды.

## Инварианты

- Dev compose не требует HTTPS.
- Production не использует Django `runserver`.
- Секреты и secure flags задаются через env, а не зашиваются в код.
- Static/media volumes явно описаны в production runtime.

## Связанные конфликты

- `C037` — local dev stand vs production HTTPS.
