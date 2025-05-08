from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = "Устанавливает Telegram Webhook"

    def handle(self, *args, **kwargs):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        site_url = settings.SITE_URL
        webhook_url = f"{site_url}/api/telegram/webhook/"

        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        response = requests.get(api_url, params={"url": webhook_url})

        self.stdout.write(self.style.SUCCESS("Устанавливаем webhook..."))
        self.stdout.write(f"--> URL: {webhook_url}")
        self.stdout.write(f" Ответ Телеграм:")
        self.stdout.write(str(response.json()))