# API Сервис заказа товаров

## Описание проекта

API сервис предоставляет возможность заказа товаров из нескольких магазинов. Каталог товаров, информация о ценах и наличии загружаются из YAML файлов единого формата.

### Основные возможности:
- Регистрация и авторизация пользователей (покупателей и магазинов)
- Загрузка товаров магазинами через YAML файлы
- Просмотр каталога товаров с фильтрацией
- Управление корзиной
- Оформление заказов
- Email уведомления о статусе заказов
- **Расширенная админка Django для управления всеми аспектами магазина**
- **Асинхронная обработка задач через Celery**

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
│   └── admin/
│       ├── import_products.html  # Страница импорта
│       └── custom_index.html     # Главная админки
├── data/                  # Примеры YAML файлов
│   ├── shop1.yaml        # Данные магазина "Связной"
│   ├── shop2.yaml        # Данные магазина "DNS"
│   └── shop3.yaml        # Данные магазина "М.Видео"
├── Dockerfile             # Конфигурация Docker образа
├── docker-compose.yml     # Конфигурация Docker сервисов
├── .dockerignore         # Исключения для Docker
├── requirements.txt       # Зависимости Python
├── manage.py             # Утилита управления Django
└── README_PROJECT.md     # Документация проекта
```

## Установка и запуск

### 1. Клонировать репозиторий:
```bash
git clone <url>
cd netology_pd_diplom
```

### 2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установить зависимости:
```bash
pip install -r requirements.txt
```

### 4. Установить и запустить Redis:
```bash
# Ubuntu/Debian/WSL2
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Проверка работы Redis
redis-cli ping
# Должен ответить: PONG
```

### 5. Настроить базу данных:

#### Для PostgreSQL:
```bash
# Создать базу данных
sudo -u postgres psql
CREATE DATABASE diplom_db;
CREATE USER diplom_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE diplom_db TO diplom_user;
\q
```

Обновить `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'diplom_db',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Выполнить миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

### 8. Загрузить тестовые данные:
```bash
python manage.py load_shop_data data/shop1.yaml --user_email shop1@example.com
python manage.py load_shop_data data/shop2.yaml --user_email shop2@example.com
python manage.py load_shop_data data/shop3.yaml --user_email shop3@example.com
```

### 9. Запуск проекта:

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
```

### Результаты тестов:
При успешном прохождении всех тестов вы увидите:
```
.......
----------------------------------------------------------------------
Ran 7 tests in X.XXXs
OK
```

Каждая точка означает успешно пройденный тест.

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

2. **Запустите все сервисы**:
```bash
# Для новых версий Docker (28.x и выше)
docker compose up --build

# Или запустить в фоновом режиме
docker compose up -d --build

# Для старых версий используйте docker-compose (с дефисом)
```

3. **Выполните миграции** (в новом терминале):
```bash
docker compose exec web python manage.py migrate
```

4. **Создайте суперпользователя**:
```bash
docker compose exec web python manage.py createsuperuser
```

5. **Загрузите тестовые данные**:
```bash
docker compose exec web python manage.py load_shop_data data/shop1.yaml --user_email shop1@example.com
docker compose exec web python manage.py load_shop_data data/shop2.yaml --user_email shop2@example.com
docker compose exec web python manage.py load_shop_data data/shop3.yaml --user_email shop3@example.com
```

### Доступ к сервисам:
- **Django приложение**: http://localhost:8000
- **Админка**: http://localhost:8000/admin/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

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
```

## Решение проблем

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

### Очистка всех товаров:
```bash
python manage.py shell
>>> from backend.models import ProductInfo, Product, ProductParameter
>>> ProductParameter.objects.all().delete()
>>> ProductInfo.objects.all().delete()
>>> Product.objects.all().delete()
>>> exit()
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

## TODO (продвинутая часть)
- [x] Настроить расширенную админку
- [x] Интегрировать Celery для асинхронных задач
- [x] Добавить тесты
- [x] Настроить Docker
- [x] Добавить документацию API (Swagger)