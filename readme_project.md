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

## Структура проекта

```
netology_pd_diplom/
├── backend/                # Основное приложение
│   ├── models.py          # Модели данных
│   ├── views.py           # API views
│   ├── serializers.py     # Сериализаторы DRF
│   ├── urls.py            # URL маршруты
│   ├── signals.py         # Сигналы для отправки email
│   └── admin.py           # Админ панель
├── netology_pd_diplom/    # Настройки проекта
│   ├── settings.py
│   └── urls.py
├── data/                  # Примеры YAML файлов
└── requirements.txt       # Зависимости
```

## Установка и запуск

1. Клонировать репозиторий:
```bash
git clone <url>
cd netology_pd_diplom
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Выполнить миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустить сервер:
```bash
python manage.py runserver
```

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
- `POST /api/v1/partner/update` - Загрузка прайса
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

## TODO (продвинутая часть)
- [ ] Настроить расширенную админку
- [ ] Интегрировать Celery для асинхронных задач
- [ ] Добавить тесты
- [ ] Настроить Docker
- [ ] Добавить документацию API (Swagger)