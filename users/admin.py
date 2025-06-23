from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):


    readonly_fields = ('telegram_verification_token',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Telegram info', {
            'fields': (
                'telegram_id',
                'username_telegram',
                'telegram_chat_id',
                'is_verified_by_telegram',
                'telegram_verification_token',
            )
        }),
        ('Роль пользователя', {
            'fields': ('role',)
        }),
    )

    list_display = BaseUserAdmin.list_display + (
        'telegram_id',
        'username_telegram',
        'telegram_chat_id',
        'is_verified_by_telegram',
        'telegram_verification_token',
        'role',
    )

    list_filter = BaseUserAdmin.list_filter + (
        'is_verified_by_telegram',
        'role',  # 👈 фильтрация по ролям
    )

    search_fields = BaseUserAdmin.search_fields + (
        'telegram_id',
        'username_telegram',
        'telegram_chat_id',
    )
