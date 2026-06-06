# HeritageProject-Back

### Требования


- Python 3.11 или выше
- PostgreSQL (локально или Docker)
- Redis (опционально, для кеширования/задач)

### Шаги для локального запуска

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Zoomish-Inc/HeritageProject-Back.git
cd HeritageProject-Back

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env под свои настройки (база, ключ и т.д.)
```

Опциональные переменные для Redis-кэша API (`GET /api/v1/heritage/`):

| Переменная | Описание | Пример |
|------------|----------|--------|
| `REDIS_URL` | URL Redis (Render Key Value / локальный Redis) | `redis://localhost:6379/0` |
| `ENVIRONMENT` | Префикс ключей кэша `{env}:heritage:...` | `dev`, `production` |
| `DATABASE_URL` | PostgreSQL (Aiven / Render) | `postgres://...` |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | Aiven PostgreSQL (альтернатива DATABASE_URL) | см. Aiven Console |
| `FRONTEND_BASE_URL` | Базовый URL для `/images/...` при seed | `https://heritage-project-front.vercel.app` |
| `SEED_MOCK_HERITAGE` | Запуск seed при билде (`false` чтобы отключить) | `true` (по умолчанию в build.sh) |

Без `REDIS_URL` API работает как раньше — данные читаются из PostgreSQL/SQLite.

На Render: создайте **Key Value** instance, добавьте `REDIS_URL` и `ENVIRONMENT=production` в env web-сервиса.

```bash
# 5. Применить миграции
python manage.py migrate

# 6. Загрузить моковые данные (идемпотентно)
python manage.py seed_mock_heritage

# 7. Запустить сервер разработки
python manage.py runserver
```

### Как обновлять OpenAPI схему (`openapi.yaml`) при изменении serializers
Проект использует **drf-spectacular**. Файл `openapi.yaml` хранится в репозитории и генерируется автоматически.

После правок в `views/serializers` обновляйте схему командой из корня проекта:

```bash
python manage.py spectacular --file openapi.yaml
```

После этого закоммитьте обновлённый `openapi.yaml`.

### Кэш list/detail (BE-18)

- Ключи: `list:v3`, `detail:{slug}:v3`, TTL 3600 с
- Инвалидация при save/delete в Admin (HeritageObject и вложенные сущности)
- Заголовок ответа `X-Cache: HIT|MISS` для отладки
- При недоступном Redis — fallback на БД без 500

```bash
curl -i http://127.0.0.1:8000/api/v1/heritage/
```

### Seed моковых данных

```bash
python manage.py seed_mock_heritage          # пропустит, если 6 объектов уже есть
python manage.py seed_mock_heritage --force  # перезалить
```

На Render seed вызывается из `build.sh` после `migrate`.

### Keep-alive для Aiven + Render free tier

Render **Cron Jobs платные**. На free tier внешний монитор шлёт пустой `GET` на `/api/app` каждые **10 минут** — этого достаточно, чтобы будить Render web и Aiven PostgreSQL.

**URL:** `https://heritageproject-back.onrender.com/api/app`

**Ответ:** `204 No Content` (тело пустое). Внутри — `SELECT 1`, UPDATE `DbHeartbeat`, SELECT по `HeritageObject`.

Резервный ping из репозитория: [`.github/workflows/db-keepalive.yml`](.github/workflows/db-keepalive.yml) (тот же URL, каждые 10 минут).

Диагностика БД/Redis — отдельно: `GET /api/v1/health/`.

Локально вручную:

```bash
python manage.py keep_db_alive
```

