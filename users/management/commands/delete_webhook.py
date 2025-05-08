from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):

    help = "Удаляет Telegram Webhook"

    def handle(self, *args, **kwargs):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"

        response = requests.get(api_url)

        self.stdout.write(self.style.SUCCESS("Удаление webhook..."))
        self.stdout.write("Ответ Telegram:")
        self.stdout.write(str(response.json()))