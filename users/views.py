from django.shortcuts import render
import time
import hmac, hashlib
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# users/views.py

import hashlib, hmac
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class TelegramLoginView(APIView):
    # теперь обрабатываем и POST, и GET
    def handle_auth(self, data):
        # копируем логику проверки подписи и создания пользователя
        received_hash = data.pop("hash", None)
        secret = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        auth_data = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        if hmac.new(secret, auth_data.encode(), hashlib.sha256).hexdigest() != received_hash:
            return Response({"error": "invalid hash"}, status=403)

        telegram_id = data["id"]
        user, _ = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": f"tg_{telegram_id}",
                "first_name": data.get("first_name", ""),
                "username_telegram": data.get("username", ""),
            }
        )
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})

    def post(self, request):
        return self.handle_auth(request.data.copy())

    def get(self, request):
        return self.handle_auth(request.GET.copy())


class ResendTelegramVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.telegram_chat_id:
            return Response({'error': 'У пользователя не указан chat_id Telegram'}, status=400)

        message = (
            f"Привет, {user.username or 'друг'}!\n"
            f"Твой токен подтверждения: '{user.telegram_verification_token}'\n\n"
            f"Отправь этот токен нашему боту или нажми на кнопку /verify {user.telegram_verification_token}"
        )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': user.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = request.post(url, json=payload)
            response.raise_for_status()
        except request.exceptions.RequestExcertion as e:
            return Response({"error": "Ошибка при отправке в Telegram", "details": str(e)}, status=500)

        return Response({"message": "Токен отправлен в Telegram"})
