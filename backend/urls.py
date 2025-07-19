"""
API endpoints для backend приложения.

Структура API:
- /partner/* - endpoints для магазинов-партнеров
- /user/* - endpoints для управления пользователями
- /categories, /shops, /products - публичные endpoints для просмотра каталога
- /basket - управление корзиной
- /order - управление заказами
"""
from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from backend.views import PartnerUpdate, RegisterAccount, LoginAccount, CategoryView, ShopView, ProductInfoView, \
    BasketView, \
    AccountDetails, ContactView, OrderView, PartnerState, PartnerOrders, ConfirmAccount

app_name = 'backend'

urlpatterns = [
    # Партнерские endpoints (для магазинов)
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),  # Загрузка прайса
    path('partner/state', PartnerState.as_view(), name='partner-state'),  # Управление статусом магазина
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),  # Просмотр заказов магазина

    # Управление пользователями
    path('user/register', RegisterAccount.as_view(), name='user-register'),  # Регистрация
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),  # Подтверждение email
    path('user/details', AccountDetails.as_view(), name='user-details'),  # Профиль пользователя
    path('user/contact', ContactView.as_view(), name='user-contact'),  # Управление контактами
    path('user/login', LoginAccount.as_view(), name='user-login'),  # Авторизация
    path('user/password_reset', reset_password_request_token, name='password-reset'),  # Запрос сброса пароля
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),  # Подтверждение сброса

    # Публичные endpoints
    path('categories', CategoryView.as_view(), name='categories'),  # Список категорий
    path('shops', ShopView.as_view(), name='shops'),  # Список магазинов
    path('products', ProductInfoView.as_view(), name='shops'),  # Поиск товаров

    # Работа с заказами
    path('basket', BasketView.as_view(), name='basket'),  # Корзина
    path('order', OrderView.as_view(), name='order'),  # Заказы
]