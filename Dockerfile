FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' /app/docker/entrypoint.sh \
    && chmod +x /app/docker/entrypoint.sh \
    && DJANGO_SECRET_KEY=build-collectstatic-only python manage.py collectstatic --noinput \
    && mkdir -p /app/media \
    && useradd --create-home --uid 1000 app \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
