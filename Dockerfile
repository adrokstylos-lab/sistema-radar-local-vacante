FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY config ./config
COPY migrations ./migrations
COPY alembic.ini ./

EXPOSE 8000

# Aplica migraciones y arranca la API (que también sirve el dashboard en /).
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
