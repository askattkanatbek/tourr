from django.shortcuts import render
import time, requests, hmac, hashlib, uuid, json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import TelegramLoginSerializer, RegisterWithChatSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def send_message(chat_id, text):
    return requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": text}
    )


class TelegramLoginView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description='Telegram ID'),
            openapi.Parameter('username', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description='Telegram username'),
            openapi.Parameter('first_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description='Имя пользователя'),
            openapi.Parameter('hash', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True, description='Telegram hash'),
        ],
        responses={
            200: openapi.Response(description="Успешная авторизация", examples={"application/json": {"access": "jwt_access_token", "refresh": "jwt_refresh_token"}}),
            400: openapi.Response(description="Ошибка авторизации")
        },
        operation_summary="Авторизация через Telegram (GET)",
        operation_description="Принимает параметры через URL и возвращает JWT токены."
    )
    def get(self, request):
        data = request.GET.copy()
        telegram_id = data.get("id")
        username = data.get("username")
        first_name = data.get("first_name")
        hash_ = data.get("hash")

        user, _ = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username_telegram": username,
                "first_name": first_name,
                "username": f"tg_{telegram_id}",
            }
        )

        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

    @swagger_auto_schema(
        request_body=TelegramLoginSerializer,
        responses={
            200: openapi.Response(description="Успешная авторизация", examples={"application/json": {"access": "jwt_access_token", "refresh": "jwt_refresh_token"}}),
            400: openapi.Response(description="Неверные данные")
        },
        operation_summary="Авторизация через Telegram (POST)",
        operation_description="Принимает данные Telegram и возвращает JWT токены."
    )
    def post(self, request):
        serializer = TelegramLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telegram_id = serializer.validated_data['id']
        username = serializer.validated_data['username']
        first_name = serializer.validated_data['first_name']

        user, _ = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username_telegram": username,
                "first_name": first_name,
                "username": f"tg_{telegram_id}",
            }
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })


class ResendTelegramVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Токен отправлен"),
            400: openapi.Response(description="Пользователь уже подтвержден или нет chat_id"),
            401: openapi.Response(description="Неавторизован")
        },
        operation_summary="Повторная отправка токена подтверждения",
        operation_description="Повторно отправляет токен подтверждения в Telegram."
    )
    def post(self, request):
        user = request.user

        if user.is_verified_by_telegram:
            return Response({'error': 'Пользователь уже подтвержден'}, status=400)

        if not user.telegram_chat_id:
            return Response({'error': 'Не указан chat_id'}, status=400)

        verification_command = f"/verify {user.telegram_verification_token}"
        message = (
            f"Привет, {user.username or 'друг'}!\n\n"
            f"Нажми на кнопку ниже или отправь эту команду боту вручную, чтобы подтвердить аккаунт:"
        )

        payload = {
            "chat_id": user.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "Подтвердить", "callback_data": verification_command}
                ]]
            }
        }

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json=payload
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({"error": "Ошибка при отправке", "details": str(e)}, status=500)

        return Response({"message": "Токен отправлен в Telegram"}, status=200)


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    @swagger_auto_schema(
        operation_summary="Webhook от Telegram",
        operation_description=(
            "Этот endpoint вызывается Telegram Bot API при получении новых сообщений. "
            "Обрабатывает команды /start, /verify <токен>, /getid и другие."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'update_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'message': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'chat': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'type': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'text': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
            required=['message']
        ),
        responses={
            200: openapi.Response(description="Webhook успешно обработан"),
        }
    )
    def post(self, request):
        print("🔔 Webhook получен!")
        print(json.dumps(request.data, indent=2, ensure_ascii=False))

        data = request.data
        message = data.get("message", {})
        chat = message.get("chat", {})
        text = message.get("text", "")
        chat_id = chat.get("id")

        if not text:
            return JsonResponse({"ok": True})

        if text.startswith("/start"):
            try:
                user = User.objects.get(telegram_id=chat_id)
                user.telegram_chat_id = chat_id
                user.save()
                send_message(chat_id, "👋 Привет! Я тебя запомнил.")
            except User.DoesNotExist:
                send_message(chat_id, "👋 Привет! Но я тебя пока не знаю.")

        elif text.startswith("/verify"):
            parts = text.split()
            if len(parts) != 2:
                send_message(chat_id, "❗ Неверный формат. Используй: /verify <токен>")
                return JsonResponse({"ok": True})

            token = parts[1]
            try:
                uuid_token = uuid.UUID(token)
            except ValueError:
                send_message(chat_id, "❗ Неверный токен. Это не UUID.")
                return JsonResponse({"ok": True})

            try:
                user = User.objects.get(telegram_verification_token=uuid_token)
                if str(user.telegram_chat_id) != str(chat_id):
                    send_message(chat_id, "❌ Этот токен не принадлежит вам.")
                    return JsonResponse({"ok": True})

                if user.is_verified_by_telegram:
                    send_message(chat_id, "✅ Вы уже подтвердили аккаунт.")
                    return JsonResponse({"ok": True})

                user.is_verified_by_telegram = True
                user.save()
                send_message(chat_id, "✅ Telegram-аккаунт подтвержден!")

            except User.DoesNotExist:
                send_message(chat_id, "❌ Токен не найден.")

            return JsonResponse({"ok": True})

        elif text.startswith("/getid"):
            send_message(chat_id, f"🆔 Твой chat_id: {chat_id}")
        else:
            send_message(chat_id, "🤖 Неизвестная команда. Используй /start, /verify <токен> или /getid")

        return JsonResponse({"ok": True})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Информация о пользователе", examples={
                "application/json": {
                    "id": 1,
                    "username": "askat",
                    "telegram_id": 123456,
                    "telegram_chat_id": 987654,
                    "is_verified_by_telegram": True
                }
            }),
            401: openapi.Response(description="Неавторизован")
        },
        operation_summary="Профиль пользователя",
        operation_description="Данные авторизованного пользователя (JWT токен обязателен)."
    )
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "telegram_id": user.telegram_id,
            "telegram_chat_id": user.telegram_chat_id,
            "is_verified_by_telegram": user.is_verified_by_telegram,
        })


class RegisterWithChatView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterWithChatSerializer,
        responses={
            201: openapi.Response(description="Пользователь создан, токен отправлен"),
            400: openapi.Response(description="Ошибка валидации")
        },
        operation_summary="Регистрация с chat_id",
        operation_description="Создаёт пользователя и отправляет токен в Telegram."
    )
    def post(self, request):
        serializer = RegisterWithChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        message = (
            f"Привет, {user.username}!\n"
            f"Твой токен подтверждения: `{user.telegram_verification_token}`\n\n"
            f"Отправь этот токен боту или нажми: /verify {user.telegram_verification_token}"
        )

        try:
            requests.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": user.telegram_chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
        except Exception as e:
            print("Ошибка при отправке в Telegram", e)

        return Response({
            "message": "Пользователь создан. Токен отправлен.",
            "user_id": user.id
        }, status=201)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING, description='UUID токен подтверждения')
    ],
    responses={
        200: openapi.Response(description="Пользователь подтверждён."),
        400: openapi.Response(description="Неверный токен.")
    },
    operation_summary="Подтверждение по токену",
    operation_description="Подтверждает аккаунт через ссылку с токеном."
)
@api_view(['GET'])
def verify_telegram_token(request, token):
    try:
        user = User.objects.get(telegram_verification_token=token)

        if user.is_verified_by_telegram:
            return Response({"message": "Пользователь уже подтверждён"}, status=status.HTTP_200_OK)

        user.is_verified_by_telegram = True
        user.save()
        return Response({"message": "Пользователь УСПЕШНО подтверждён"}, status=status.HTTP_200_OK)

    except (ValueError, User.DoesNotExist):
        return Response({"error": "Неверный или недействительный токен"}, status=status.HTTP_400_BAD_REQUEST)
