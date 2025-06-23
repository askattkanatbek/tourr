from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='Telegram ID')
    username_telegram = models.CharField(max_length=150, null=True, blank=True, verbose_name='Telegram username')

    telegram_chat_id = models.CharField(max_length=64, null=True, blank=True)
    telegram_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    is_verified_by_telegram = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        CONSULTANT = 'consultant', 'Консультант'
        TOUR_CREATOR = 'creator', 'Автор тура'
        CLIENT = 'client', 'Клиент'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="Роль"
    )

    def __str__(self):
        return self.username or f'tg_user_{self.telegram_id}'
