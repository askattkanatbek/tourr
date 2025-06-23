from rest_framework import  serializers
from .models import User

class TelegramLoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    hash = serializers.CharField()

class RegisterWithChatSerializer(serializers.ModelSerializer):
    chat_id = serializers.CharField(write_only=True)  # <- клиент отправляет chat_id

    class Meta:
        model = User
        fields = ['username', 'password', 'chat_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        chat_id = validated_data.pop('chat_id')

        user = User(
            username=validated_data['username'],
            telegram_chat_id=chat_id,
            is_verified_by_telegram = False
        )
        user.set_password(password)
        user.save()


        return user

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']
        read_only_fields = ['id', 'username', 'email']

