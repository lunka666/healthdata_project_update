# HealthData — Django + PostgreSQL + Docker

Учебное Django-приложение для учёта показателей здоровья. Сохраняет записи на выбор пользователя: в JSON-файлы или в PostgreSQL. Для записей БД доступны проверка дубликатов, просмотр, AJAX-поиск, редактирование и удаление.

## Стек

- Python 3.12, Django
- PostgreSQL 16
- Docker и Docker Compose
- Gunicorn
- WhiteNoise для раздачи собранных статических файлов

## Требования

Установите Docker Desktop (Windows/macOS) или Docker Engine и Docker Compose plugin (Linux). Для локальной разработки без Docker дополнительно нужен Python 3.12+.

## Быстрый запуск через Docker Compose

1. Скопируйте пример переменных окружения:

   ```bash
   cp .env.example .env
   ```

   В Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Откройте `.env` и задайте уникальные значения `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD`. Не публикуйте `.env` и не добавляйте его в Git.
3. Запустите контейнеры:

   ```bash
   docker compose up --build -d
   ```
4. Откройте http://localhost:8000/.
5. Просмотрите логи:

   ```bash
   docker compose logs -f web
   ```
6. Остановите контейнеры, сохранив данные:

   ```bash
   docker compose down
   ```

   Для полного удаления данных PostgreSQL (ОСТОРОЖНО: удалит базу) используется `docker compose down -v`.

При старте контейнер Django ожидает готовности PostgreSQL, выполняет `migrate`, `collectstatic`, затем запускает Gunicorn. Суперпользователь создаётся командой:

```bash
docker compose exec web python manage.py createsuperuser
```

## Режим разработки

Compose запускает тот же контейнерный стек. Для удобства разработки можно временно изменить `.env`:

```env
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

После изменения переменных пересоздайте web-контейнер:

```bash
docker compose up --build -d --force-recreate web
```

Изменения исходного кода попадут в контейнер после пересборки образа. Для обычной разработки без Docker можно использовать SQLite: создайте виртуальное окружение, установите `requirements.txt`, оставьте `DB_ENGINE=sqlite` (или не задавайте эту переменную), затем выполните `python manage.py migrate` и `python manage.py runserver`.

## Production

1. На сервере установите Docker Engine и Compose plugin.
2. Склонируйте репозиторий и перейдите в каталог проекта.
3. Создайте `.env` на основе `.env.example`; задайте сильный `DJANGO_SECRET_KEY`, уникальный `POSTGRES_PASSWORD`, `DJANGO_DEBUG=False`, публичное имя хоста в `DJANGO_ALLOWED_HOSTS` и HTTPS-origin в `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Запустите `docker compose up --build -d`.
5. Настройте HTTPS reverse proxy (например, Caddy или Nginx) перед портом приложения и ограничьте прямой доступ к порту приложения сетевыми правилами. Не публикуйте порт PostgreSQL наружу.
6. Настройте резервное копирование PostgreSQL (например, регулярный `pg_dump`) и проверяйте восстановление.

Compose использует Gunicorn, `DEBUG=False` (если так задано в `.env`), PostgreSQL и постоянные Docker volumes. Сам по себе Compose не настраивает домен, TLS-сертификат, firewall или резервное копирование — это отдельные операции на production-сервере.

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `DJANGO_SECRET_KEY` | Секрет Django |
| `DJANGO_DEBUG` | Режим отладки (`True`/`False`) |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые host names через запятую |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Доверенные origins через запятую, включая схему |
| `POSTGRES_DB` | Имя БД |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `WEB_PORT` | Порт приложения на хосте (по умолчанию 8000) |

`DB_ENGINE=postgres` и `POSTGRES_HOST=db` устанавливаются Compose автоматически. Если приложение запускается локально без Docker и `DB_ENGINE` не задан, используется SQLite.

## Постоянное хранение

В `docker-compose.yml` настроены volumes:

- `postgres_data` — файлы PostgreSQL;
- `static_volume` — результат `collectstatic`;
- `json_data` — пользовательские JSON-файлы.

Эти данные сохраняются после пересоздания контейнеров. Не используйте `docker compose down -v`, если хотите сохранить базу и JSON.

## Перенос данных из старой SQLite-базы PythonAnywhere

Перенос выполняется из локальной копии старой SQLite-базы в PostgreSQL. Перед началом сделайте резервную копию `db.sqlite3` на PythonAnywhere и скачайте её в корень проекта рядом с `manage.py`.

1. Установите зависимости проекта локально (`python -m pip install -r requirements.txt`).
2. Создайте `.env` и задайте пароль PostgreSQL.
3. Убедитесь, что в корне проекта находится старая `db.sqlite3`.
4. Запустите скрипт из корня проекта в Git Bash / Linux / macOS:

   ```bash
   bash scripts/migrate_sqlite_to_postgres.sh
   ```

Скрипт временно выбирает SQLite через `DB_ENGINE=sqlite`, экспортирует записи модели `records.HealthRecord` командой `dumpdata`, запускает PostgreSQL и Django, копирует fixture в контейнер и импортирует записи командой `loaddata`. Миграции схемы выполняются при старте Django-контейнера.

Если в старой SQLite-базе есть другие модели с важными данными, их нужно экспортировать отдельно, изменив аргумент `dumpdata`. Перед повторным импортом проверьте, нет ли уже загруженных записей: импорт fixture с существующими первичными ключами может привести к конфликтам. После переноса сравните количество записей и проверьте выборку, поиск, редактирование и удаление. Не удаляйте исходную SQLite-копию, пока перенос не проверен.

**JSON-файлы не находятся в SQLite.** Если их тоже нужно перенести с PythonAnywhere, отдельно скачайте каталог `data_storage/json/` и скопируйте его содержимое в постоянный Docker volume `json_data` (например, временно подключив volume к вспомогательному контейнеру или выполнив копирование через контейнер приложения).

## Проверка приложения

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py shell -c "from records.models import HealthRecord; print(HealthRecord.objects.count())"
```

Проверьте в браузере оба источника хранения, предотвращение дубликатов в PostgreSQL, AJAX-поиск, редактирование и удаление записей.

## Git и секреты

Файл `.env` исключён через `.gitignore`; для репозитория предоставлен только `.env.example` с демонстрационными значениями. Перед публикацией проверьте:

```bash
git status
git check-ignore .env
```

Не помещайте в репозиторий реальные пароли, ключи, дампы БД и персональные данные.
