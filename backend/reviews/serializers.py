from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'booking', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_booking(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You can only review your own bookings.")
        return value
