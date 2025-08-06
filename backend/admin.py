"""
Конфигурация админ-панели Django.

Продвинутая версия с фильтрами, поиском, inline-редактированием
и кастомными действиями для управления заказами.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models import F, Sum
from django.utils.html import format_html

from backend.models import (
    Category,
    ConfirmEmailToken,
    Contact,
    Order,
    OrderItem,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями.

    Расширяет стандартный UserAdmin для работы с кастомной моделью User.
    """

    model = User

    # Настройка полей для редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password", "type")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "company", "position")}),
        (
            "Права доступа",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "type", "is_active")}),
    )

    # Поля, отображаемые в списке пользователей
    list_display = ("email", "first_name", "last_name", "type", "company", "is_active", "is_staff")
    list_filter = ("type", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "company")
    ordering = ("email",)


class ProductInfoInline(admin.TabularInline):
    """
    Inline для редактирования информации о товаре в разных магазинах
    """

    model = ProductInfo
    extra = 1
    fields = ("shop", "model", "external_id", "quantity", "price", "price_rrc")


class ProductParameterInline(admin.TabularInline):
    """
    Inline для редактирования параметров товара
    """

    model = ProductParameter
    extra = 1


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Админка для магазинов.
    """

    list_display = ("name", "user", "state", "get_products_count", "get_orders_count")
    list_filter = ("state",)
    search_fields = ("name", "user__email")
    readonly_fields = ("get_products_count", "get_orders_count")

    def get_products_count(self, obj):
        """Количество товаров в магазине"""
        return obj.product_infos.count()

    get_products_count.short_description = "Товаров"

    def get_orders_count(self, obj):
        """Количество заказов магазина"""
        return OrderItem.objects.filter(product_info__shop=obj).values("order").distinct().count()

    get_orders_count.short_description = "Заказов"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админка для категорий товаров.
    """

    list_display = ("name", "get_shops_count", "get_products_count")
    search_fields = ("name",)
    filter_horizontal = ("shops",)  # Удобный виджет для M2M

    def get_shops_count(self, obj):
        """Количество магазинов в категории"""
        return obj.shops.count()

    get_shops_count.short_description = "Магазинов"

    def get_products_count(self, obj):
        """Количество товаров в категории"""
        return obj.products.count()

    get_products_count.short_description = "Товаров"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Админка для товаров.
    """

    list_display = ("name", "category", "get_shops_count", "get_min_price", "get_total_quantity")
    list_filter = ("category",)
    search_fields = ("name",)
    inlines = [ProductInfoInline]

    def get_shops_count(self, obj):
        """В скольких магазинах есть товар"""
        return obj.product_infos.count()

    get_shops_count.short_description = "Магазинов"

    def get_min_price(self, obj):
        """Минимальная цена"""
        min_price = obj.product_infos.aggregate(min_price=models.Min("price"))["min_price"]
        return f"{min_price} руб." if min_price else "-"

    get_min_price.short_description = "Мин. цена"

    def get_total_quantity(self, obj):
        """Общее количество на складах"""
        total = obj.product_infos.aggregate(total=models.Sum("quantity"))["total"]
        return total or 0

    get_total_quantity.short_description = "Всего на складах"


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Админка для информации о товарах в магазинах.
    """

    list_display = ("product", "shop", "model", "quantity", "price", "price_rrc", "get_margin")
    list_filter = ("shop", "product__category")
    search_fields = ("product__name", "model", "external_id")
    inlines = [ProductParameterInline]
    readonly_fields = ("get_margin",)

    def get_margin(self, obj):
        """Рассчет маржи"""
        if obj.price_rrc and obj.price:
            margin = ((obj.price_rrc - obj.price) / obj.price_rrc) * 100
            return f"{margin:.1f}%"
        return "-"

    get_margin.short_description = "Маржа"


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Админка для параметров товаров.
    """

    list_display = ("name", "get_usage_count")
    search_fields = ("name",)

    def get_usage_count(self, obj):
        """Сколько раз используется параметр"""
        return obj.product_parameters.count()

    get_usage_count.short_description = "Использований"


class OrderItemInline(admin.TabularInline):
    """
    Inline для позиций заказа
    """

    model = OrderItem
    extra = 0
    readonly_fields = ("get_product_name", "get_shop", "get_price", "get_sum")
    fields = ("product_info", "get_product_name", "get_shop", "quantity", "get_price", "get_sum")

    def get_product_name(self, obj):
        return obj.product_info.product.name if obj.product_info else "-"

    get_product_name.short_description = "Товар"

    def get_shop(self, obj):
        return obj.product_info.shop.name if obj.product_info else "-"

    get_shop.short_description = "Магазин"

    def get_price(self, obj):
        return f"{obj.product_info.price} руб." if obj.product_info else "-"

    get_price.short_description = "Цена"

    def get_sum(self, obj):
        if obj.product_info and obj.quantity:
            return f"{obj.product_info.price * obj.quantity} руб."
        return "-"

    get_sum.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админка для заказов с расширенным функционалом.
    """

    list_display = ("id", "dt", "user", "state", "get_total_sum", "contact", "colored_state")
    list_filter = ("state", "dt")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("dt", "get_total_sum", "get_order_details")
    inlines = [OrderItemInline]
    date_hierarchy = "dt"
    ordering = ("-dt",)

    # Поля для редактирования
    fields = ("user", "state", "contact", "dt", "get_total_sum", "get_order_details")

    # Массовые действия для изменения статусов
    actions = ["make_confirmed", "make_assembled", "make_sent", "make_delivered", "make_canceled"]

    def get_total_sum(self, obj):
        """Общая сумма заказа"""
        total = obj.ordered_items.aggregate(total=Sum(F("quantity") * F("product_info__price")))["total"]
        return f"{total} руб." if total else "0 руб."

    get_total_sum.short_description = "Сумма"

    def get_order_details(self, obj):
        """Детали заказа в удобном формате"""
        items = []
        for item in obj.ordered_items.all():
            items.append(
                f"{item.product_info.product.name} "
                f"({item.product_info.shop.name}) - "
                f"{item.quantity} шт. × {item.product_info.price} руб."
            )
        return format_html("<br>".join(items)) if items else "Нет товаров"

    get_order_details.short_description = "Состав заказа"

    def colored_state(self, obj):
        """Цветовая индикация статуса"""
        colors = {
            "basket": "gray",
            "new": "blue",
            "confirmed": "green",
            "assembled": "orange",
            "sent": "purple",
            "delivered": "darkgreen",
            "canceled": "red",
        }
        return format_html(
            '<span style="color: {};">{}</span>', colors.get(obj.state, "black"), obj.get_state_display()
        )

    colored_state.short_description = "Статус"

    # Действия для изменения статуса
    def make_confirmed(self, request, queryset):
        updated = queryset.update(state="confirmed")
        self.message_user(request, f"{updated} заказов подтверждено.")

    make_confirmed.short_description = "Подтвердить выбранные заказы"

    def make_assembled(self, request, queryset):
        updated = queryset.update(state="assembled")
        self.message_user(request, f"{updated} заказов собрано.")

    make_assembled.short_description = "Отметить как собранные"

    def make_sent(self, request, queryset):
        updated = queryset.update(state="sent")
        self.message_user(request, f"{updated} заказов отправлено.")

    make_sent.short_description = "Отметить как отправленные"

    def make_delivered(self, request, queryset):
        updated = queryset.update(state="delivered")
        self.message_user(request, f"{updated} заказов доставлено.")

    make_delivered.short_description = "Отметить как доставленные"

    def make_canceled(self, request, queryset):
        updated = queryset.update(state="canceled")
        self.message_user(request, f"{updated} заказов отменено.")

    make_canceled.short_description = "Отменить выбранные заказы"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Админка для контактов пользователей.
    """

    list_display = ("user", "city", "street", "house", "phone", "get_full_address")
    list_filter = ("city",)
    search_fields = ("user__email", "city", "phone")

    def get_full_address(self, obj):
        """Полный адрес"""
        parts = [obj.city, obj.street, obj.house]
        if obj.structure:
            parts.append(f"корп. {obj.structure}")
        if obj.building:
            parts.append(f"стр. {obj.building}")
        if obj.apartment:
            parts.append(f"кв. {obj.apartment}")
        return ", ".join(parts)

    get_full_address.short_description = "Полный адрес"


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    """
    Админка для токенов подтверждения email.
    """

    list_display = ("user", "key", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "key")
    readonly_fields = ("key", "created_at")


# Настройка заголовков админки
admin.site.site_header = "Администрирование магазина"
admin.site.site_title = "Магазин"
admin.site.index_title = "Панель управления"
