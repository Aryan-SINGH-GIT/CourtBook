
from rest_framework import serializers

class DailyAvailabilityQuerySerializer(serializers.Serializer):
    """Serializer for daily availability query"""
    date = serializers.DateField()


class TimeSlotSerializer(serializers.Serializer):
    """Serializer for a single time slot status"""
    time = serializers.TimeField()
    is_booked = serializers.BooleanField()
    booking_id = serializers.IntegerField(allow_null=True)
    is_user_booking = serializers.BooleanField(default=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class CourtDailyAvailabilitySerializer(serializers.Serializer):
    """Serializer for a court's daily schedule"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    slots = TimeSlotSerializer(many=True)
