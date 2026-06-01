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

# 5. Применить миграции
python manage.py migrate

# 6. Загрузить начальные данные (опционально, но полезно)
python seed.py

# 7. Запустить сервер разработки
python manage.py runserver
