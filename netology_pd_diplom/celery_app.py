"""
Конфигурация Celery для проекта.
"""
import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

# Создаем экземпляр Celery
app = Celery('netology_pd_diplom')

# Загружаем настройки из Django settings с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Тестовая задача для отладки"""
    print(f'Request: {self.request!r}')