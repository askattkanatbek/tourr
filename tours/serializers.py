from rest_framework import serializers
from .models import Tour, TourCategory

class TourSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fileds = ('created_by, created_at')


class TourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory
        fields = '__all__'


def validate(self, data):
    if data['end_date'] < data['start_date']:
        raise serializers.ValidationError("Дата окончания не может быть раньше даты начала")
    return data