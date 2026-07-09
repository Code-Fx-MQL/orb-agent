#!/bin/sh
set -e

PORT="${PORT:-8501}"
export PORT

mkdir -p /app/data/memory /app/data/audit /app/data/cache

exec streamlit run src/orb_agent/ui/app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT}" \
  --browser.gatherUsageStats=false \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false