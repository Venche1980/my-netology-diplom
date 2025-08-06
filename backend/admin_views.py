# backend/admin_views.py
"""
Дополнительные views для админки.
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import redirect, render

from backend.models import Shop
from backend.tasks import do_import


@staff_member_required
def import_products_view(request):
    """
    View для импорта товаров через админку.

    Доступен только для staff пользователей.
    """
    if request.method == "POST":
        url = request.POST.get("url")
        shop_id = request.POST.get("shop_id")

        if not url or not shop_id:
            messages.error(request, "Необходимо указать URL и магазин")
            return redirect("admin:import_products")

        # Валидация URL
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError:
            messages.error(request, "Неверный формат URL")
            return redirect("admin:import_products")

        # Получаем магазин
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, "Магазин не найден")
            return redirect("admin:import_products")

        # Запускаем импорт
        task = do_import.delay(url, shop.user.id)

        messages.success(request, f'Импорт запущен для магазина "{shop.name}". Task ID: {task.id}')

        return redirect("admin:backend_productinfo_changelist")

    # GET запрос - показываем форму
    shops = Shop.objects.filter(state=True)
    context = {
        "title": "Импорт товаров",
        "shops": shops,
    }
    return render(request, "admin/import_products.html", context)
