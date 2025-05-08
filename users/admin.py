from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Telegram info', {
            'fields':(
                'telegram_id',
                'username_telegram',
                'telegram_chat_id',

                'is_verified_by_telegram',

            )
        }),
    )

    list_display = BaseUserAdmin.list_display + (
        'telegram_id',
        'username_telegram',
        'telegram_chat_id',
        'is_verified_by_telegram',
        'telegram_verification_token',
    )

    list_filter = BaseUserAdmin.list_filter + (
        'is_verified_by_telegram',
    )

    search_fields = BaseUserAdmin.search_fields + (
        'telegram_id',
        'username_telegram',
        'telegram_chat_id',
    )