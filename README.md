# django shop project
Структура проекта:
/
├── src/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── common/
│   │   ├── users/
│   │   ├── catalog/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── reviews/
│   │   ├── payments/
│   │   └── api/
│   │
│   ├── templates/
│   ├── static/
│   └── media/
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── business-rules.md
│   ├── api.md
│   ├── development.md
│   ├── testing.md
│   └── decisions/
│       ├── 0001-use-poetry.md
│       ├── 0002-session-cart.md
│       ├── 0003-jwt-for-api.md
│       └── 0004-order-transaction.md
│
├── tests/
├── docker/
├── env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── manage.py
└── README.md