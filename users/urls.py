from django.urls import path
from users.views import (
    TelegramLoginView,
    ResendTelegramVerificationView,
    TelegramWebhookView,
    MeView,
    RegisterWithChatView,
    verify_telegram_token,
    UserListView,
    UserDetailView
)
from django.views.generic import TemplateView

urlpatterns = [
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram_login'),
    path('telegram/resend-verification/', ResendTelegramVerificationView.as_view(), name='resend-verification'),
    path('login/telegram/', TemplateView.as_view(template_name='login_with_telegram.html')),
    path('telegram/webhook/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('verify-telegram/<uuid:token>/', verify_telegram_token, name='verify-telegram'),
    path('me/', MeView.as_view(), name='me'),
    path('register/', RegisterWithChatView.as_view(), name='register-with-chat'),
    path('users/', UserListView.as_view(), name='admin-users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
]
