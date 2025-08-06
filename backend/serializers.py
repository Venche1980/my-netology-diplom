# Верстальщик
from rest_framework import serializers

from backend.models import Category, Contact, Order, OrderItem, Product, ProductInfo, ProductParameter, Shop, User


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для контактов пользователя.

    Скрывает поле user при выводе данных для безопасности.
    """

    class Meta:
        model = Contact
        fields = ("id", "city", "street", "house", "structure", "building", "apartment", "user", "phone")
        read_only_fields = ("id",)
        extra_kwargs = {"user": {"write_only": True}}  # user не отображается в ответе API


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя.

    Включает связанные контакты пользователя.
    """

    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "company", "position", "contacts")
        read_only_fields = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий товаров.

    Простой сериализатор для вывода списка категорий.
    """

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для магазинов.

    Показывает основную информацию о магазине и его статус.
    """

    class Meta:
        model = Shop
        fields = (
            "id",
            "name",
            "state",
        )
        read_only_fields = ("id",)


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товаров.

    Использует StringRelatedField для отображения названия категории
    вместо её ID.
    """

    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = (
            "name",
            "category",
        )


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для параметров товара.

    Отображает название параметра и его значение для конкретного товара.
    """

    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = (
            "parameter",
            "value",
        )


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о товаре в магазине.

    Включает вложенные данные о самом товаре и его параметрах.
    Используется для отображения полной информации о товаре.
    """

    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = (
            "id",
            "model",
            "product",
            "shop",
            "quantity",
            "price",
            "price_rrc",
            "product_parameters",
        )
        read_only_fields = ("id",)


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для позиций заказа.

    Используется для создания и обновления позиций в корзине.
    Поле order скрыто при выводе для безопасности.
    """

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_info",
            "quantity",
            "order",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"order": {"write_only": True}}


class OrderItemCreateSerializer(OrderItemSerializer):
    """
    Расширенный сериализатор для позиций заказа.

    Включает полную информацию о товаре для отображения в заказе.
    """

    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заказов.

    Включает:
    - Все позиции заказа с полной информацией о товарах
    - Общую сумму заказа (вычисляемое поле)
    - Контактную информацию для доставки
    """

    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    # Вычисляемое поле - общая сумма заказа
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "ordered_items",
            "state",
            "dt",
            "total_sum",
            "contact",
        )
        read_only_fields = ("id",)
