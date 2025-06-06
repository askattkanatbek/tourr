from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from users.models import User


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class ResendVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='resend_user',
            password='testpass123',
            telegram_chat_id='123456789',
            is_verified_by_telegram=False
        )
        self.token = str(AccessToken.for_user(self.user))
        self.url = '/api/telegram/resend-verification/'
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    @patch("users.tasks.requests.post")
    def test_successful_resend_verification(self, mock_post):
        response = self.client.post(self.url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_post.called)

    def test_resend_with_missing_chat_id(self):
        self.user.telegram_chat_id = None
        self.user.save()

        response = self.client.post(self.url, **self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('chat_id', response.json().get('error', '').lower())

    def test_resend_when_already_verified(self):
        self.user.is_verified_by_telegram = True
        self.user.save()

        response = self.client.post(self.url, **self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('уже подтвержден', response.json().get('error', '').lower())
