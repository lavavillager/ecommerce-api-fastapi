#!/usr/bin/env bash
# Применяет миграции, загружает seed-данные и запускает переданную команду.
set -e

echo "⏳ Ожидание базы данных..."
python - <<'PY'
import time
import sqlalchemy
from app.core.config import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL)
for attempt in range(30):
    try:
        with engine.connect():
            break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("❌ Не удалось подключиться к базе данных")
print("✅ База данных доступна")
PY

echo "⏳ Применение миграций Alembic..."
alembic upgrade head

echo "⏳ Загрузка seed-данных..."
python -m app.seed || echo "⚠️  Seed пропущен"

echo "🚀 Запуск приложения..."
exec "$@"
