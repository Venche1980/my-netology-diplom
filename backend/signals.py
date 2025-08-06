# backend/signals.py
"""
Сигналы Django для отправки уведомлений.

Модуль содержит обработчики сигналов для:
- Отправки email при регистрации пользователя
- Отправки email при сбросе пароля
- Отправки email при создании нового заказа

Использует Celery для асинхронной отправки писем.
"""
from typing import Type

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User
from backend.tasks import send_email

# Кастомные сигналы
new_user_registered = Signal()  # Срабатывает при регистрации нового пользователя
new_order = Signal()  # Срабатывает при создании нового заказа


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # Отправляем email асинхронно через Celery
    send_email.delay(
        subject=f"Password Reset Token for {reset_password_token.user}",
        message=reset_password_token.key,
        recipient_list=[reset_password_token.user.email],
    )


@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
    Отправляем письмо с подтверждением почты при создании нового пользователя.

    Срабатывает только для новых неактивных пользователей.
    Генерирует токен подтверждения и отправляет его на email.
    """
    if created and not instance.is_active:
        # Создаем или получаем токен подтверждения для пользователя
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)

        # Отправляем email асинхронно через Celery
        send_email.delay(
            subject=f"Email Confirmation Token for {instance.email}", message=token.key, recipient_list=[instance.email]
        )


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    Отправляем письмо при изменении статуса заказа.

    Вызывается вручную из view при подтверждении заказа.

    :param user_id: ID пользователя, создавшего заказ
    """
    # Получаем пользователя
    user = User.objects.get(id=user_id)

    # Отправляем email асинхронно через Celery
    send_email.delay(subject="Обновление статуса заказа", message="Заказ сформирован", recipient_list=[user.email])
