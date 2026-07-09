FROM python:3.12-slim

WORKDIR /app

ENV PORT=8501
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir -e ".[ui]"

COPY .env.example .env.example
COPY docs/ docs/
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh \
    && mkdir -p /app/data/memory /app/data/audit /app/data/cache

EXPOSE 8501

HEALTHCHECK CMD /bin/sh -c 'curl -f "http://localhost:${PORT:-8501}/_stcore/health" || exit 1'

ENTRYPOINT ["/docker-entrypoint.sh"]