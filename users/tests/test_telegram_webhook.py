from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User



class TelegramWebhookVerificationTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='to_verify',
            password='test1234',
            telegram_id = 123456789,
            telegram_chat_id = 123456789,
            is_verified_by_telegram = False
        )

    def test_successful_verification(self):
        payload = {
            "message":{
                "chat": {"id": int(self.user.telegram_chat_id)},
                "text": f"/verify {self.user.telegram_verification_token}"
            }
        }

        response = self.client.post('/api/telegram/webhook/', data=payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified_by_telegram)