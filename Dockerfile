FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install --no-cache-dir poetry && poetry install

COPY . .

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
