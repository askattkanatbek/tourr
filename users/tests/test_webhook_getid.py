from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch
from users.models import User

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class TestTelegramGetId(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.chat_id = 987654321
        self.payload = {
            "message":{
                "chat": {"id": self.chat_id},
                "text": "/getid"
            }
        }

    @patch("users.tasks.requests.post")
    def test_getid_command_sends_correct_chat_id(self, mock_post):
        response = self.client.post('/api/telegram/webhook/', data=self.payload, format='json')
        self.assertEqual(response.status_code,200)
        self.assertTrue(mock_post.called)

        sent_payload = mock_post.call_args[1]['data'] if 'data' in mock_post.call_args[1] else mock_post.call_args[1]['json']
        self.assertEqual(str(self.chat_id), str(sent_payload['chat_id']))
        self.assertIn(str(self.chat_id), sent_payload['text'])