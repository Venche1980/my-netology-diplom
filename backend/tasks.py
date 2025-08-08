"""
Асинхронные задачи Celery для приложения backend.

Модуль содержит задачи для:
- Асинхронной отправки email уведомлений
- Асинхронного импорта товаров из YAML файлов

Все задачи выполняются в фоновом режиме через Celery worker,
что позволяет избежать блокировки основного потока выполнения.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

from celery import shared_task
from requests import get
from yaml import Loader
from yaml import load as load_yaml

from backend.models import Category, Parameter, Product, ProductInfo, ProductParameter, Shop

User = get_user_model()


@shared_task
def send_email(subject, message, recipient_list):
    """
    Асинхронная отправка email через Celery.

    Используется для отправки уведомлений о регистрации, сбросе пароля,
    изменении статуса заказа и других событиях.

    Args:
        subject (str): Тема письма
        message (str): Текст письма
        recipient_list (list): Список email адресов получателей

    Returns:
        bool: True если письмо отправлено успешно, False при ошибке

    Example:
        >>> send_email.delay(
        ...     subject="Подтверждение регистрации",
        ...     message="Ваш код: 123456",
        ...     recipient_list=["user@example.com"]
        ... )
    """
    try:
        msg = EmailMultiAlternatives(
            subject=subject, body=message, from_email=settings.EMAIL_HOST_USER, to=recipient_list
        )
        msg.send()
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {str(e)}")
        return False


@shared_task
def do_import(url, user_id):
    """
    Асинхронный импорт товаров из YAML файла.

    Загружает файл по URL, парсит YAML формат и обновляет каталог товаров магазина.
    Старые товары магазина удаляются перед импортом новых.
    После успешного импорта отправляет email уведомление.

    Args:
        url (str): URL адрес YAML файла с товарами
        user_id (int): ID пользователя-магазина

    Returns:
        dict: Словарь с результатом операции
            - status (bool): Успешность операции
            - message (str): Описание результата
            - shop (str): Название магазина
            - error (str): Описание ошибки (если есть)

    YAML Format:
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

    Example:
        >>> do_import.delay(
        ...     url="https://example.com/products.yaml",
        ...     user_id=1
        ... )
    """
    try:
        user = User.objects.get(id=user_id)

        if user.type != "shop":
            return {"status": False, "error": "Пользователь не является магазином"}

        # Загружаем файл
        stream = get(url).content
        data = load_yaml(stream, Loader=Loader)

        # Создаем или обновляем магазин
        shop, _ = Shop.objects.get_or_create(name=data["shop"], user_id=user.id)

        # Обрабатываем категории
        for category in data["categories"]:
            category_object, _ = Category.objects.get_or_create(id=category["id"], name=category["name"])
            category_object.shops.add(shop.id)
            category_object.save()

        # Удаляем старые товары
        ProductInfo.objects.filter(shop_id=shop.id).delete()

        # Загружаем новые товары
        products_created = 0
        for item in data["goods"]:
            product, _ = Product.objects.get_or_create(name=item["name"], category_id=item["category"])

            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item["id"],
                model=item["model"],
                price=item["price"],
                price_rrc=item["price_rrc"],
                quantity=item["quantity"],
                shop_id=shop.id,
            )
            products_created += 1

            # Создаем параметры товара
            for name, value in item["parameters"].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id, parameter_id=parameter_object.id, value=value
                )

        # Отправляем уведомление об успешном импорте
        send_email.delay(
            subject=f"Импорт товаров завершен - {shop.name}",
            message=f"Успешно импортировано {products_created} товаров.",
            recipient_list=[user.email],
        )

        return {"status": True, "message": f"Импортировано {products_created} товаров", "shop": shop.name}

    except Exception as e:
        return {"status": False, "error": str(e)}
