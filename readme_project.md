# API Сервис заказа товаров

## Описание проекта

API сервис предоставляет возможность заказа товаров из нескольких магазинов. Каталог товаров, информация о ценах и наличии загружаются из YAML файлов единого формата.

### Основные возможности:
- Регистрация и авторизация пользователей (покупателей и магазинов)
- Загрузка товаров магазинами через YAML файлы
- **Экспорт товаров магазина в YAML формате**
- Просмотр каталога товаров с фильтрацией
- Управление корзиной
- Оформление заказов
- Email уведомления о статусе заказов
- **Автоматическая отправка накладной администратору**
- Расширенная админка Django для управления всеми аспектами магазина
- Асинхронная обработка задач через Celery

## Структура проекта

```
netology_pd_diplom/
├── backend/                # Основное приложение
│   ├── models.py          # Модели данных
│   ├── views.py           # API views
│   ├── serializers.py     # Сериализаторы DRF
│   ├── urls.py            # URL маршруты
│   ├── signals.py         # Сигналы для отправки email
│   ├── admin.py           # Расширенная админ панель
│   ├── admin_views.py     # Дополнительные views для админки
│   ├── tasks.py           # Celery задачи
│   ├── apps.py            # Конфигурация приложения
│   ├── tests.py           # Тесты для основного функционала
│   └── management/        # Команды управления
│       └── commands/
│           └── load_shop_data.py  # Команда загрузки данных
├── netology_pd_diplom/    # Настройки проекта
│   ├── __init__.py        # Инициализация Celery
│   ├── celery_app.py      # Конфигурация Celery
│   ├── settings.py        # Настройки Django проекта
│   ├── urls.py            # Главные URL маршруты
│   └── wsgi.py            # WSGI конфигурация
├── templates/             # Шаблоны
│   ├── admin/
│   │   ├── import_products.html  # Страница импорта
│   │   └── custom_index.html     # Главная админки
│   └── email/
│       └── invoice.html           # HTML шаблон накладной
├── data/                  # Примеры YAML файлов
│   ├── shop1.yaml        # Данные магазина "Связной"
│   ├── shop2.yaml        # Данные магазина "DNS"
│   └── shop3.yaml        # Данные магазина "М.Видео"
├── .env.example          # Пример файла с переменными окружения
├── .gitignore            # Исключения для Git
├── .dockerignore         # Исключения для Docker
├── Dockerfile            # Конфигурация Docker образа
├── docker-compose.yml    # Конфигурация Docker сервисов
├── Makefile              # Команды для автоматизации
├── pyproject.toml        # Конфигурация Black и isort
├── setup.cfg             # Конфигурация flake8
├── requirements.txt      # Зависимости Python
├── manage.py             # Утилита управления Django
├── README.md             # Краткая документация
└── readme_project.md     # Полная документация проекта
```

## Установка и запуск

### Требования
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker и Docker Compose (для контейнерного запуска)

### 1. Клонировать репозиторий:
```bash
git clone <url>
cd netology_pd_diplom
```

### 2. Настройка переменных окружения:
```bash
# Копировать пример файла переменных окружения
cp .env.example .env

# Отредактировать .env и заполнить реальными значениями:
# - SECRET_KEY - секретный ключ Django
# - Параметры базы данных
# - Параметры email
# - ADMIN_EMAIL - email администратора для получения накладных
nano .env
```

### 3. Создать виртуальное окружение (для локальной разработки):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 4. Установить зависимости:
```bash
pip install -r requirements.txt
```

### 5. Установить и запустить Redis (для локальной разработки):
```bash
# Ubuntu/Debian/WSL2
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Проверка работы Redis
redis-cli ping
# Должен ответить: PONG
```

### 6. Настроить базу данных:

#### Для PostgreSQL:
```bash
# Создать базу данных
sudo -u postgres psql
CREATE DATABASE diplom_db;
CREATE USER diplom_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE diplom_db TO diplom_user;
\q
```

### 7. Выполнить миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

### 9. Загрузить тестовые данные:
```bash
python manage.py load_shop_data data/shop1.yaml --user_email shop1@example.com
python manage.py load_shop_data data/shop2.yaml --user_email shop2@example.com
python manage.py load_shop_data data/shop3.yaml --user_email shop3@example.com
```

### 10. Запуск проекта:

Для полноценной работы нужно запустить в разных терминалах:

**Терминал 1 - Django сервер:**
```bash
python manage.py runserver
```

**Терминал 2 - Celery worker:**
```bash
celery -A netology_pd_diplom.celery_app:app worker -l info
# или
python -m celery -A netology_pd_diplom.celery_app:app worker -l info
```

**Терминал 3 - Redis (если не запущен как сервис):**
```bash
redis-server
```

## Docker

Проект настроен для запуска в Docker контейнерах.

### Что включено:
- **PostgreSQL** - база данных
- **Redis** - брокер сообщений для Celery
- **Django** - основное приложение
- **Celery Worker** - обработчик асинхронных задач

### Запуск с Docker:

1. **Установите Docker и Docker Compose**:
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Проверьте установку: `docker --version`

2. **Настройте переменные окружения**:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите все сервисы**:
```bash
# Сборка и запуск контейнеров
docker compose up --build

# Или запустить в фоновом режиме
docker compose up -d --build
```

4. **Выполните миграции** (в новом терминале):
```bash
docker compose exec web python manage.py migrate
```

5. **Создайте суперпользователя**:
```bash
docker compose exec web python manage.py createsuperuser
```

6. **Загрузите тестовые данные**:
```bash
docker compose exec web python manage.py load_shop_data data/shop1.yaml --user_email shop1@example.com
docker compose exec web python manage.py load_shop_data data/shop2.yaml --user_email shop2@example.com
docker compose exec web python manage.py load_shop_data data/shop3.yaml --user_email shop3@example.com
```

### Доступ к сервисам:
- **Django приложение**: http://localhost:8000
- **Админка**: http://localhost:8000/admin/
- **API документация (Swagger)**: http://localhost:8000/api/v1/swagger/

### Полезные команды Docker:
```bash
# Посмотреть логи
docker compose logs -f

# Остановить все контейнеры
docker compose down

# Остановить и удалить volumes (БД)
docker compose down -v

# Запустить тесты
docker compose exec web python manage.py test

# Войти в контейнер
docker compose exec web bash

# Django shell в контейнере
docker compose exec web python manage.py shell
```

## Расширенная админка Django

Админка доступна по адресу: http://127.0.0.1:8000/admin/

### Возможности админки:
- **Управление пользователями**: фильтры по типу (магазин/покупатель), поиск, управление правами
- **Управление магазинами**: просмотр количества товаров и заказов, управление статусом
- **Управление товарами**: 
  - Inline редактирование вариантов товара в разных магазинах
  - Отображение минимальной цены и общего количества
  - Поиск и фильтрация по категориям
- **Управление заказами**:
  - Цветовая индикация статусов
  - Массовые действия для изменения статусов
  - Inline редактирование позиций заказа
  - Автоматический подсчет суммы заказа
  - Фильтры по статусу и дате
  - Автоматическая отправка накладной при изменении статуса
- **Управление контактами**: полный адрес, поиск по городу
- **Импорт товаров из YAML**: асинхронная загрузка через Celery

### Массовые действия для заказов:
- Подтвердить выбранные заказы
- Отметить как собранные
- Отметить как отправленные
- Отметить как доставленные
- Отменить выбранные заказы

## Celery и асинхронные задачи

### Реализованные задачи:
- `send_email` - асинхронная отправка email уведомлений
- `do_import` - асинхронный импорт товаров из YAML файлов
- `send_invoice_to_admin` - отправка накладной администратору при оформлении заказа

### Импорт товаров через админку:
1. На главной странице админки нажмите "Импорт товаров из YAML"
2. Выберите магазин
3. Укажите URL файла YAML (можно использовать GitHub raw URL)
4. Нажмите "Начать импорт"
5. Задача будет выполнена асинхронно через Celery

## API Endpoints

### Авторизация
- `POST /api/v1/user/register` - Регистрация
- `POST /api/v1/user/register/confirm` - Подтверждение email
- `POST /api/v1/user/login` - Вход
- `POST /api/v1/user/password_reset` - Сброс пароля

### Пользователь
- `GET/POST /api/v1/user/details` - Профиль пользователя
- `GET/POST/PUT/DELETE /api/v1/user/contact` - Управление контактами

### Каталог
- `GET /api/v1/categories` - Список категорий
- `GET /api/v1/shops` - Список магазинов
- `GET /api/v1/products` - Поиск товаров

### Заказы
- `GET/POST/PUT/DELETE /api/v1/basket` - Корзина
- `GET/POST /api/v1/order` - Заказы

### Для магазинов
- `POST /api/v1/partner/update` - Загрузка прайса (асинхронно через Celery)
- `GET/POST /api/v1/partner/state` - Статус приема заказов
- `GET /api/v1/partner/orders` - Заказы магазина
- **`GET /api/v1/partner/export`** - Экспорт товаров в YAML

## Отправка накладной администратору

### Описание
При оформлении заказа автоматически отправляется HTML-накладная на email администратора с полной информацией о заказе.

### Возможности:
- Автоматическая отправка при оформлении заказа через API
- Отправка при изменении статуса заказа на "Новый" через админку
- Красивый HTML-шаблон с таблицей товаров
- Асинхронная отправка через Celery

### Настройка:
1. **Установите email администратора в .env:**
```bash
ADMIN_EMAIL=admin@example.com
```

2. **Шаблон накладной находится в:**
```
templates/email/invoice.html
```

### Что содержит накладная:
- Информация о заказе (номер, дата, статус)
- Данные покупателя (имя, email, компания)
- Адрес доставки
- Таблица товаров с колонками:
  - Название товара
  - Магазин
  - Модель
  - Количество
  - Цена за единицу
  - Сумма по позиции
- Общая сумма заказа

### Когда отправляется накладная:
1. **При оформлении заказа через API** - когда покупатель переводит корзину в статус "new"
2. **При изменении статуса в админке** - когда администратор меняет статус на "Новый"
3. **Вручную через Django shell:**
```python
from backend.tasks import send_invoice_to_admin
send_invoice_to_admin(order_id)
```

### Реализация:
- **Celery задача:** `backend.tasks.send_invoice_to_admin`
- **Сигналы:** `backend.signals.new_order_signal` и `order_status_changed`
- **Шаблон:** `templates/email/invoice.html`

### Важно:
- Для отправки email необходимо отключить VPN (если используется)
- Email настройки должны быть корректно указаны в .env файле
- Celery worker должен быть запущен для асинхронной отправки

## Экспорт товаров

### Описание
Магазины могут экспортировать свой каталог товаров в YAML формате для резервного копирования или переноса данных.

### Использование

#### 1. Через API:
```bash
# Получить токен авторизации
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"email": "shop@example.com", "password": "yourpassword"}'

# Экспортировать товары (замените YOUR_TOKEN на полученный токен)
curl -X GET http://localhost:8000/api/v1/partner/export \
  -H "Authorization: Token YOUR_TOKEN" \
  -o products.yaml
```

#### 2. Через Python:
```python
import requests

# Авторизация
login = requests.post('http://localhost:8000/api/v1/user/login', json={
    'email': 'shop@example.com',
    'password': 'yourpassword'
})

if login.status_code == 200:
    token = login.json()['Token']
    
    # Экспорт товаров
    export = requests.get(
        'http://localhost:8000/api/v1/partner/export',
        headers={'Authorization': f'Token {token}'}
    )
    
    if export.status_code == 200:
        with open('exported_products.yaml', 'wb') as f:
            f.write(export.content)
        print("Товары успешно экспортированы!")
    else:
        print(f"Ошибка: {export.text}")
```

### Формат экспортированного файла
Экспортированный YAML файл имеет тот же формат, что и для импорта:
```yaml
shop: Название магазина
categories:
  - id: 1
    name: Категория
goods:
  - id: 1
    category: 1
    model: model_name
    name: Название товара
    price: 1000
    price_rrc: 1200
    quantity: 10
    parameters:
      "Параметр": значение
```

### Совместимость
Экспортированный файл полностью совместим с функцией импорта, что позволяет:
- Создавать резервные копии каталога
- Переносить товары между магазинами
- Использовать для тестирования

## Формат YAML для загрузки товаров

```yaml
shop: Название магазина
categories:
  - id: 1
    name: Категория
goods:
  - id: 1
    category: 1
    model: model_name
    name: Название товара
    price: 1000
    price_rrc: 1200
    quantity: 10
    parameters:
      "Параметр": значение
```

## Тестирование

Проект включает набор тестов для проверки основного функционала.

### Что покрывают тесты:
- **Регистрация и авторизация**: создание нового пользователя, вход в систему
- **Работа с корзиной**: добавление товаров, проверка авторизации
- **Заказы**: создание и получение заказов
- **Загрузка товаров**: проверка прав доступа (только для магазинов)
- **API endpoints**: проверка доступа к защищенным endpoints

### Запуск тестов:
```bash
# Запустить все тесты
python manage.py test

# Запустить с подробным выводом
python manage.py test --verbosity=2

# Запустить конкретный тест
python manage.py test backend.tests.UserRegistrationTest

# Запустить с сохранением тестовой БД (для отладки)
python manage.py test --keepdb

# В Docker
docker compose exec web python manage.py test
```

### Результаты тестов:
При успешном прохождении всех тестов вы увидите:
```
.......
----------------------------------------------------------------------
Ran 7 tests in X.XXXs
OK
```

## API Документация (Swagger)

Проект включает автоматически генерируемую документацию API с помощью Swagger/OpenAPI.

### Доступ к документации:
После запуска проекта документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/api/v1/swagger/ - интерактивная документация
- **ReDoc**: http://localhost:8000/api/v1/docs/ - альтернативный формат документации

### Возможности Swagger:
- Просмотр всех доступных endpoints
- Описание параметров запросов
- Примеры ответов
- **Интерактивное тестирование API прямо из браузера**
- Автоматическая генерация из кода

### Как использовать:
1. Откройте http://localhost:8000/api/v1/swagger/
2. Выберите нужный endpoint
3. Нажмите "Try it out"
4. Заполните параметры
5. Нажмите "Execute"
6. Увидите реальный ответ от API

## Качество кода

Проект следует стандартам PEP8 и использует инструменты для поддержания качества кода:

### Инструменты форматирования:
- **Black** - автоматическое форматирование кода
- **isort** - сортировка импортов
- **flake8** - проверка соответствия PEP8

### Использование:
```bash
# Установка инструментов разработки
pip install black flake8 isort

# Автоматическое форматирование
black backend/ netology_pd_diplom/ --line-length 120
isort backend/ netology_pd_diplom/

# Проверка кода
flake8 backend/ netology_pd_diplom/ --max-line-length=120 --exclude=migrations
```

### Конфигурация:
- `pyproject.toml` - настройки Black и isort
- `setup.cfg` - настройки flake8
- Максимальная длина строки: 120 символов

## Документация кода

Весь код проекта полностью документирован:
- **Docstrings** для всех классов и методов
- **Комментарии** для сложной логики
- **Type hints** где необходимо
- **Примеры использования** в docstrings

### Стиль документации:
- Google-style docstrings
- Описание параметров и возвращаемых значений
- Примеры использования для публичных API

## Безопасность

### Переменные окружения
Все чувствительные данные хранятся в переменных окружения:
- Секретный ключ Django
- Пароли базы данных
- Учетные данные email
- Email администратора для накладных

### Файл .env
1. Скопируйте `.env.example` в `.env`
2. Заполните все переменные реальными значениями
3. **НИКОГДА** не коммитьте `.env` файл в репозиторий

### Переменные окружения:
```bash
# Django
SECRET_KEY=          # Секретный ключ Django
DEBUG=               # True/False - режим отладки

# База данных (локальная)
DB_NAME=             # Имя базы данных
DB_USER=             # Пользователь БД
DB_PASSWORD=         # Пароль БД
DB_HOST=             # Хост БД
DB_PORT=             # Порт БД

# Email
EMAIL_HOST=          # SMTP сервер (smtp.gmail.com)
EMAIL_PORT=          # Порт (587 для TLS)
EMAIL_USE_TLS=       # True/False
EMAIL_USE_SSL=       # True/False
EMAIL_HOST_USER=     # Email для отправки писем
EMAIL_HOST_PASSWORD= # Пароль приложения (не обычный пароль!)
ADMIN_EMAIL=         # Email администратора для накладных

# Docker PostgreSQL
POSTGRES_DB=         # Имя БД в Docker
POSTGRES_USER=       # Пользователь PostgreSQL
POSTGRES_PASSWORD=   # Пароль PostgreSQL
```

### Важные замечания по email:
- **Gmail**: требует пароль приложения (создается в настройках безопасности Google аккаунта)
- **VPN**: при использовании VPN отправка email может не работать из-за блокировки SMTP
- **WSL2**: известны проблемы с SSL/TLS handshake, рекомендуется отключать VPN

## Решение проблем

### Если email не отправляется:
```bash
# Проверьте, что VPN отключен
# Проверьте настройки в .env
# Для Gmail используйте пароль приложения, не обычный пароль
# Проверьте логи Celery
docker compose logs celery
```

### Если Celery не запускается:
```bash
# Попробуйте альтернативный запуск
python -m celery -A netology_pd_diplom.celery_app:app worker -l info
```

### Если Redis не работает:
```bash
# Проверить статус
sudo service redis-server status

# Перезапустить
sudo service redis-server restart
```

### Если Docker контейнеры не запускаются:
```bash
# Проверить логи
docker compose logs web
docker compose logs celery

# Пересобрать образы
docker compose down
docker compose build --no-cache
docker compose up
```

### Если Docker buildx не найден:
```bash
# Обновите Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Или используйте DOCKER_BUILDKIT=0
DOCKER_BUILDKIT=0 docker compose up --build
```

### Очистка всех товаров:
```bash
python manage.py shell
>>> from backend.models import ProductInfo, Product, ProductParameter
>>> ProductParameter.objects.all().delete()
>>> ProductInfo.objects.all().delete()
>>> Product.objects.all().delete()
>>> exit()
```

## Выполненные задачи (продвинутая часть)
- [x] Настроить расширенную админку
- [x] Интегрировать Celery для асинхронных задач
- [x] Добавить тесты
- [x] Настроить Docker
- [x] Добавить документацию API (Swagger)
- [x] Вынести чувствительные данные в переменные окружения
- [x] Привести код в соответствие с PEP8
- [x] Добавить полную документацию (docstrings)
- [x] Реализовать экспорт товаров
- [x] Реализовать отправку накладной администратору ✅

## Авторы

Проект выполнен в рамках дипломной работы курса "Python-разработчик" от Нетологии.