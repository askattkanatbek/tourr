from django.urls import path
from users.views import (
    TelegramLoginView,
    ResendTelegramVerificationView,
)
from django.views.generic import TemplateView
from users.views import TelegramWebhookView, MeView, RegisterWithChatView, verify_telegram_token

urlpatterns = [
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram_login'),
    path('telegram/resend-verification/', ResendTelegramVerificationView.as_view(), name='resend-verification'),
    path('login/telegram/', TemplateView.as_view(template_name='login_with_telegram.html')),
    path('telegram/webhook/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('me/', MeView.as_view(), name='me'),
    path('register/', RegisterWithChatView.as_view(), name='register-with-chat'),
    path('verify-telegram/<uuid:token>/', verify_telegram_token, name='verify-telegram')

]
