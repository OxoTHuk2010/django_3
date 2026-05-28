#!/bin/sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
DOMAIN="${DOMAIN:-}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"
HTTPS_TEMPLATE_DIR="${HTTPS_TEMPLATE_DIR:-./docker/nginx/templates}"
BOOTSTRAP_TEMPLATE_DIR="${BOOTSTRAP_TEMPLATE_DIR:-./.deploy/nginx-templates}"

compose() {
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

require_file() {
    if [ ! -f "$1" ]; then
        echo "Required file is missing: $1"
        exit 1
    fi
}

has_certificate() {
    compose run --rm --entrypoint sh certbot -c \
        "test -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem && test -f /etc/letsencrypt/live/$DOMAIN/privkey.pem"
}

issue_certificate() {
    if [ "$LETSENCRYPT_EMAIL" = "" ]; then
        echo "LETSENCRYPT_EMAIL is required for first HTTPS bootstrap"
        exit 1
    fi

    mkdir -p "$BOOTSTRAP_TEMPLATE_DIR"
    cp docker/nginx/templates/http-only.conf.example "$BOOTSTRAP_TEMPLATE_DIR/default.conf.template"

    export NGINX_TEMPLATES_DIR="$BOOTSTRAP_TEMPLATE_DIR"
    compose up -d --build db web nginx

    compose run --rm --entrypoint certbot certbot \
        certonly \
        --webroot \
        -w /var/www/certbot \
        --email "$LETSENCRYPT_EMAIL" \
        -d "$DOMAIN" \
        --agree-tos \
        --no-eff-email
}

require_file "$ENV_FILE"
require_file "$COMPOSE_FILE"

if [ "$DOMAIN" = "" ]; then
    echo "DOMAIN is required"
    exit 1
fi

compose config --quiet
compose build web

if ! has_certificate; then
    issue_certificate
fi

export NGINX_TEMPLATES_DIR="$HTTPS_TEMPLATE_DIR"
compose up -d --build
compose exec -T web python manage.py check

if command -v curl >/dev/null 2>&1; then
    curl --fail --silent --show-error --location "https://$DOMAIN/api/schema/" >/dev/null
fi
