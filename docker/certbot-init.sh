#!/bin/sh
set -eu

if [ "${DOMAIN:-}" = "" ]; then
    echo "DOMAIN is required"
    exit 1
fi

if [ "${LETSENCRYPT_EMAIL:-}" = "" ]; then
    echo "LETSENCRYPT_EMAIL is required"
    exit 1
fi

docker compose -f docker-compose.prod.yml run --rm certbot \
    certonly \
    --webroot \
    -w /var/www/certbot \
    --email "$LETSENCRYPT_EMAIL" \
    -d "$DOMAIN" \
    --agree-tos \
    --no-eff-email
