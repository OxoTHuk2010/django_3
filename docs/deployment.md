# Деплой

Документ описывает production deploy на ВМ с self-hosted GitHub Actions runner.

## Домен

Production-домен не хранится в репозитории. Значение задаётся через GitHub Variable `PRODUCTION_DOMAIN`.

После успешного деплоя приложение должно быть доступно по HTTPS на домене из `PRODUCTION_DOMAIN`.

## Workflow

Deploy workflow находится в `.github/workflows/deploy-production.yml`.

Запуск:

- вручную через `workflow_dispatch`;
- автоматически после push в `main`.

Workflow выполняет:

- checkout репозитория;
- создание локального `.env.production` из GitHub Secrets;
- проверку `docker-compose.prod.yml`;
- сборку production image;
- первый выпуск Let's Encrypt сертификата при отсутствии сертификата;
- запуск production stack через Docker Compose;
- `python manage.py check` внутри контейнера `web`;
- HTTPS smoke-check `/api/schema/`.

## Первый HTTPS bootstrap

Первый запуск выполняется в два шага:

1. Поднимается временная HTTP-only конфигурация Nginx для ACME challenge.
2. Выпускается сертификат Let's Encrypt, после чего включается штатная HTTPS-конфигурация.

Повторные деплои используют уже выпущенный сертификат и выполняют обычный `docker compose up -d --build`.

## Требуемые GitHub Secrets

Добавить в GitHub Environment или Repository Secrets:

- `PRODUCTION_SECRET_KEY`
- `PRODUCTION_DB_PASSWORD`

## Требуемые GitHub Variables

Добавить в GitHub Environment или Repository Variables:

- `PRODUCTION_DOMAIN`
- `PRODUCTION_DB_NAME`
- `PRODUCTION_DB_USER`
- `LETSENCRYPT_EMAIL`

Значения не должны храниться в репозитории.

## Требования к ВМ

На ВМ должны быть установлены:

- Docker;
- Docker Compose plugin;
- GitHub Actions self-hosted runner;
- доступ runner-пользователя к Docker daemon.

Снаружи должны быть доступны порты:

- `80/tcp`;
- `443/tcp`.

DNS-запись из `PRODUCTION_DOMAIN` должна указывать на публичный IP ВМ.

## Ручная проверка на ВМ

После деплоя:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml exec web python manage.py check
curl -I "https://$PRODUCTION_DOMAIN/"
curl -I "https://$PRODUCTION_DOMAIN/api/schema/"
```

## Откат

Минимальный откат выполняется повторным запуском workflow на предыдущем коммите или ручным checkout нужной ревизии на runner с повторным запуском deploy script.

База данных хранится в Docker volume `postgres_data` и не удаляется при обычном redeploy.
