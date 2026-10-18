# Учёт показателей здоровья — Django, SQLite и JSON

Учебный проект: можно вводить данные через форму и выбирать хранение в JSON или SQLite; смотреть данные из любого источника; искать записи в SQLite через AJAX; редактировать и удалять записи базы данных. Загруженные JSON-файлы проверяются перед тем, как остаться на сервере.

> Используйте только вымышленные данные. Проект не предназначен для хранения реальных медицинских карт.

## Запуск локально

Требуется Python 3.10+.

```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD: venv\Scripts\activate.bat
# macOS/Linux: source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000/.

## Функции

- Выбор сохранения формы: JSON-файл или SQLite.
- Проверка дубликатов при записи в SQLite (совпадают все поля записи, включая симптомы).
- Выбор источника данных на странице просмотра.
- AJAX-поиск по ФИО, группе крови и симптомам в SQLite.
- Редактирование с серверной проверкой формы и удаление записей SQLite.
- Загрузка JSON до 2 МБ с проверкой структуры и значений.
- Bootstrap 5 интерфейс.

## Миграции и администрирование

Миграция `records/migrations/0001_initial.py` создаёт таблицу `HealthRecord`.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Панель администратора: `/admin/`.

## Публикация на PythonAnywhere (бесплатный аккаунт)

1. Создайте аккаунт на https://www.pythonanywhere.com/ и откройте Bash-консоль.
2. Загрузите проект в GitHub и клонируйте репозиторий в консоли:
   ```bash
   git clone https://github.com/ВАШ-ЛОГИН/ВАШ-РЕПОЗИТОРИЙ.git
   cd ВАШ-РЕПОЗИТОРИЙ/healthdata_project
   ```
   Если папка проекта находится в корне репозитория, переходите прямо в неё.
3. Создайте окружение и установите зависимости:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
4. На вкладке **Web** нажмите **Add a new web app** → **Manual configuration** → выберите ту же версию Python.
5. Укажите путь к виртуальному окружению и исходной папке проекта.
6. Откройте WSGI configuration file и замените его содержимое, исправив путь к проекту и имя пользователя:
   ```python
   import os, sys
   project = '/home/ВАШ-ЛОГИН/ВАШ-РЕПОЗИТОРИЙ/healthdata_project'
   if project not in sys.path:
       sys.path.insert(0, project)
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthdata.settings')
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
7. В разделе **Web → Environment variables** задайте:
   - `DJANGO_SECRET_KEY` — длинный случайный секретный ключ;
   - `DJANGO_DEBUG` — `False`;
   - `DJANGO_ALLOWED_HOSTS` — например, `ВАШ-ЛОГИН.pythonanywhere.com`.
8. После изменения переменных окружения перезагрузите веб-приложение кнопкой **Reload**.

SQLite-файл и JSON-данные должны находиться в каталоге, доступном для записи вашему аккаунту. На бесплатном тарифе доступность, ограничения и поддерживаемые версии Python могут меняться — сверяйтесь с актуальными настройками аккаунта PythonAnywhere.

## Git-коммиты

```bash
git add records/models.py records/migrations records/admin.py
git commit -m "Добавлена модель записей здоровья и миграция"
git add records/forms.py records/views.py records/urls.py records/templates
 git commit -m "Добавлены SQLite, поиск AJAX и управление записями"
git add healthdata/settings.py requirements.txt README.md
git commit -m "Подготовлена конфигурация и инструкция развёртывания"
git push
```

Если проект уже подключён к Git, не создавайте новый репозиторий — отправьте эти изменения в существующий.
