from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from users.models import User


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class TelegramRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register-with-chat')
        self.data = {
            "username": "askat_test",
            "password": "revendetta1",
            "chat_id": "123456789"
        }

    @patch("users.tasks.requests.post")
    def test_register_and_send_verification_token(self, mock_post):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="askat_test")
        self.assertEqual(str(user.telegram_chat_id), self.data["chat_id"])
        self.assertFalse(user.is_verified_by_telegram)
        self.assertTrue(mock_post.called)

        call_args = mock_post.call_args[1]['json']
        self.assertIn("/verify", call_args['text'])
        self.assertIn(str(user.telegram_verification_token), call_args["text"])
