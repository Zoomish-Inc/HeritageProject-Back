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
| `VERCEL_DEPLOY_HOOK_URL` | Deploy Hook URL фронтенда на Vercel | `https://api.vercel.com/v1/integrations/deploy/...` |

Без `REDIS_URL` API работает как раньше — данные читаются из PostgreSQL/SQLite.

На Render: создайте **Key Value** instance, добавьте `REDIS_URL` и `ENVIRONMENT=production` в env web-сервиса.

```bash
# 5. Применить миграции
python manage.py migrate

# 6. Запустить сервер разработки
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

### 3D-туры (Google Drive)

Туры больше не хранятся в git фронтенда. Vercel build скачивает manifest с бэкенда и разворачивает zip с Google Drive.

**Workflow для редактора:**

1. Экспорт 3DVista → zip (полный Web, в архиве есть `lib/tdvplayer.js`)
2. Загрузить zip на Google Drive → доступ «Все, у кого есть ссылка»
3. В админке объекта: `slug` = имя папки тура на фронте (например `zhenskaya-gimnaziya`)
4. Вставить ID файла или share-ссылку в `tourGoogleDriveFileId`
5. Включить `tourPublished`, Save → автодеплой фронта через Deploy Hook (~2–5 мин)

`tourEntryUrl` опционален: если пусто, фронт подставит `/tour-packs/{slug}/index.htm`.

**Manifest API (для Vercel build):**

```bash
curl http://127.0.0.1:8000/api/v1/tour-packs/
```

```json
{
  "success": true,
  "data": [
    {
      "slug": "zhenskaya-gimnaziya",
      "googleDriveFileId": "1Zk97dKNV0c3gxm-x-AMQHBblXmrc50bU",
      "updatedAt": "2026-06-06T12:00:00Z"
    }
  ]
}
```

На Render добавьте `VERCEL_DEPLOY_HOOK_URL` (Vercel → Project → Settings → Git → Deploy Hooks).

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

