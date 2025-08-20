"""
Дополнительные views для админ-панели Django.

Содержит кастомные представления для расширения функциональности админки,
включая страницу импорта товаров из YAML файлов.
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
    View для асинхронного импорта товаров через админку.

    Предоставляет интерфейс для загрузки товаров из внешних YAML файлов.
    Импорт выполняется асинхронно через Celery для избежания таймаутов.

    Доступен только для staff пользователей.

    GET:
        Отображает форму выбора магазина и ввода URL файла.
        Показывает список активных магазинов и поле для ввода URL.

    POST:
        Валидирует данные и запускает асинхронную задачу импорта.
        После запуска перенаправляет на список товаров.

    Args:
        request (HttpRequest): HTTP запрос

    Returns:
        HttpResponse: Отрендеренная страница или редирект

    Template:
        admin/import_products.html

    Context:
        - title (str): Заголовок страницы
        - shops (QuerySet): Список активных магазинов

    Messages:
        - error: При ошибке валидации или отсутствии данных
        - success: При успешном запуске импорта с ID задачи
    """
    if request.method == "POST":
        # Получаем данные из формы
        url = request.POST.get("url")
        shop_id = request.POST.get("shop_id")

        # Проверяем наличие обязательных полей
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

        # Перенаправляем на список товаров
        return redirect("admin:backend_productinfo_changelist")

    # GET запрос - показываем форму импорта
    # Получаем только активные магазины (state=True)
    shops = Shop.objects.filter(state=True)
    context = {
        "title": "Импорт товаров",
        "shops": shops,
    }
    return render(request, "admin/import_products.html", context)
