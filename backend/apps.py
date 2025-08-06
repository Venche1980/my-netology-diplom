"""
Конфигурация приложения backend.
"""

from django.apps import AppConfig


class BackendConfig(AppConfig):
    """
    Конфигурация Django приложения backend.

    Содержит основную бизнес-логику API сервиса для заказа товаров.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "backend"

    def ready(self):
        """
        Метод вызывается при загрузке приложения.

        Здесь импортируем сигналы, чтобы они были зарегистрированы.
        """
        # Импорт сигналов необходим для их регистрации
        import backend.signals  # noqa: F401
