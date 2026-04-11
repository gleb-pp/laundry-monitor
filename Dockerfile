FROM python:3.13-slim
RUN groupadd -r appuser && useradd -r -g appuser -m appuser
WORKDIR /app
ENV HOME=/home/appuser

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --only main --no-root --no-interaction --no-ansi
COPY --chown=appuser:appuser . .
USER appuser
