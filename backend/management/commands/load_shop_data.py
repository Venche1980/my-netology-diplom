# backend/management/commands/load_shop_data.py
"""
Команда для загрузки данных магазина из YAML файла.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from yaml import Loader
from yaml import load as load_yaml

from backend.models import Category, Parameter, Product, ProductInfo, ProductParameter, Shop

User = get_user_model()


class Command(BaseCommand):
    help = "Загрузка данных магазина из YAML файла"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Путь к YAML файлу")
        parser.add_argument("--user_email", type=str, help="Email пользователя-магазина", default="shop@example.com")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        user_email = options["user_email"]

        # Создаем или получаем пользователя
        user, created = User.objects.get_or_create(
            email=user_email, defaults={"first_name": "Shop", "last_name": "Owner", "type": "shop", "is_active": True}
        )
        if created:
            user.set_password("shoppassword")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Создан пользователь {user_email}"))

        # Читаем YAML файл
        with open(file_path, "r", encoding="utf-8") as file:
            data = load_yaml(file, Loader=Loader)

        # Создаем магазин
        shop, _ = Shop.objects.get_or_create(name=data["shop"], user_id=user.id)
        self.stdout.write(self.style.SUCCESS(f'Магазин "{shop.name}" готов'))

        # Загружаем категории
        for category in data["categories"]:
            category_object, _ = Category.objects.get_or_create(id=category["id"], name=category["name"])
            category_object.shops.add(shop.id)
            category_object.save()

        # Удаляем старые товары магазина
        ProductInfo.objects.filter(shop_id=shop.id).delete()

        # Загружаем товары
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

            # Загружаем параметры товара
            for name, value in item["parameters"].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id, parameter_id=parameter_object.id, value=value
                )

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(data["goods"])} товаров'))
