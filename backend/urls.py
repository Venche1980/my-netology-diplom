"""
API endpoints для backend приложения.

Структура API:
- /partner/* - endpoints для магазинов-партнеров
- /user/* - endpoints для управления пользователями
- /categories, /shops, /products - публичные endpoints для просмотра каталога
- /basket - управление корзиной
- /order - управление заказами
"""

from django.urls import path, re_path

from django_rest_passwordreset.views import reset_password_confirm, reset_password_request_token
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from backend.views import (
    AccountDetails,
    BasketView,
    CategoryView,
    ConfirmAccount,
    ContactView,
    LoginAccount,
    OrderView,
    PartnerOrders,
    PartnerState,
    PartnerUpdate,
    ProductInfoView,
    RegisterAccount,
    ShopView,
)

app_name = "backend"

# Настройка Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Сервис заказа товаров",
        default_version="v1",
        description="API для заказа товаров из нескольких магазинов",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Документация API
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Партнерские endpoints (для магазинов)
    path("partner/update", PartnerUpdate.as_view(), name="partner-update"),  # Загрузка прайса
    path("partner/state", PartnerState.as_view(), name="partner-state"),  # Управление статусом магазина
    path("partner/orders", PartnerOrders.as_view(), name="partner-orders"),  # Просмотр заказов магазина
    # Управление пользователями
    path("user/register", RegisterAccount.as_view(), name="user-register"),  # Регистрация
    path("user/register/confirm", ConfirmAccount.as_view(), name="user-register-confirm"),  # Подтверждение email
    path("user/details", AccountDetails.as_view(), name="user-details"),  # Профиль пользователя
    path("user/contact", ContactView.as_view(), name="user-contact"),  # Управление контактами
    path("user/login", LoginAccount.as_view(), name="user-login"),  # Авторизация
    path("user/password_reset", reset_password_request_token, name="password-reset"),  # Запрос сброса пароля
    path("user/password_reset/confirm", reset_password_confirm, name="password-reset-confirm"),  # Подтверждение сброса
    # Публичные endpoints
    path("categories", CategoryView.as_view(), name="categories"),  # Список категорий
    path("shops", ShopView.as_view(), name="shops"),  # Список магазинов
    path("products", ProductInfoView.as_view(), name="shops"),  # Поиск товаров
    # Работа с заказами
    path("basket", BasketView.as_view(), name="basket"),  # Корзина
    path("order", OrderView.as_view(), name="order"),  # Заказы
]
