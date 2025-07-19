"""
Конфигурация админ-панели Django.

Регистрирует все модели приложения в админке с базовыми настройками.
TODO: В продвинутой части нужно будет добавить:
- Фильтры и поиск
- Inline редактирование связанных объектов
- Кастомные действия для управления заказами
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями.

    Расширяет стандартный UserAdmin для работы с кастомной моделью User.
    """
    model = User

    # Настройка полей для редактирования пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Поля, отображаемые в списке пользователей
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Админка для магазинов.
    TODO: Добавить list_display, list_filter, search_fields
    """
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админка для категорий товаров.
    TODO: Добавить filter_horizontal для поля shops
    """
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Админка для товаров.
    TODO: Добавить поиск по названию и фильтр по категориям
    """
    pass


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Админка для информации о товарах в магазинах.
    TODO: Добавить inline для ProductParameter
    """
    pass


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Админка для параметров товаров.
    TODO: Добавить поиск по названию
    """
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    """
    Админка для значений параметров товаров.
    TODO: Добавить фильтры по товару и параметру
    """
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админка для заказов.
    TODO: Добавить:
    - list_display с датой, пользователем, статусом и суммой
    - list_filter по статусу и дате
    - inline для OrderItem
    - actions для смены статусов
    """
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админка для позиций в заказах.
    TODO: Обычно не нужна отдельно, лучше использовать inline в Order
    """
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Админка для контактов пользователей.
    TODO: Добавить поиск по городу и пользователю
    """
    pass


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    """
    Админка для токенов подтверждения email.

    Отображает пользователя, токен и время создания.
    """
    list_display = ('user', 'key', 'created_at',)