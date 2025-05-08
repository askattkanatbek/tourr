from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
import uuid


class VerifyTelegramTokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='123456',
            telegram_verification_token=uuid.uuid4(),
            is_verified_by_telegram=False
        )
        self.url = f'/api/verify-telegram/{self.user.telegram_verification_token}/'

    def test_successful_verification(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успешно", response.json()["message"].lower())

    def test_already_verified(self):
        self.user.is_verified_by_telegram = True
        self.user.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("уже подтвержден", response.json()["message"].lower())

    def test_invalid_uuid(self):
        response = self.client.get('/api/verify-telegram/not-a-valid-uuid/')
        self.assertIn(response.status_code, [400, 404])  # Django может вернуть 404
        # Не вызываем .json(), если ответ HTML

    def test_nonexistent_token(self):
        random_uuid = uuid.uuid4()
        response = self.client.get(f'/api/verify-telegram/{random_uuid}/')
        self.assertIn(response.status_code, [400, 404])
        if response.headers.get('Content-Type') == 'application/json':
            self.assertIn("неверный", response.json()["error"].lower())
