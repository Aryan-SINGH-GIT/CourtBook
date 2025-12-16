"""
Serializers for REST API endpoints
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from resources.models import Court, Equipment, Coach, CoachAvailability
from pricing.models import PricingRule, BasePrice
from bookings.models import Booking, BookingResource
from datetime import date, time


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CourtSerializer(serializers.ModelSerializer):
    """Serializer for Court model"""
    class Meta:
        model = Court
        fields = ['id', 'name', 'court_type', 'is_active']


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'total_quantity', 'available_quantity']


class CoachSerializer(serializers.ModelSerializer):
    """Serializer for Coach model"""
    class Meta:
        model = Coach
        fields = ['id', 'name', 'is_active']


class CoachAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for Coach Availability"""
    coach_name = serializers.CharField(source='coach.name', read_only=True)
    
    class Meta:
        model = CoachAvailability
        fields = ['id', 'coach', 'coach_name', 'date', 'start_time', 'end_time']


class PricingRuleSerializer(serializers.ModelSerializer):
    """Serializer for Pricing Rules"""
    class Meta:
        model = PricingRule
        fields = ['id', 'rule_type', 'value', 'is_percentage', 'is_active']


class BasePriceSerializer(serializers.ModelSerializer):
    """Serializer for Base Prices"""
    class Meta:
        model = BasePrice
        fields = ['id', 'resource_type', 'price', 'is_active']


class BookingResourceSerializer(serializers.ModelSerializer):
    """Serializer for Booking Resources"""
    resource_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BookingResource
        fields = ['id', 'resource_type', 'resource_id', 'quantity', 'resource_name']
    
    def get_resource_name(self, obj):
        """Get the name of the associated resource"""
        resource = obj.get_resource_object()
        return resource.name if resource else f"{obj.resource_type} #{obj.resource_id}"


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer for listing bookings"""
    user = UserSerializer(read_only=True)
    resources = BookingResourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'date', 'start_time', 'end_time',
            'total_price', 'status', 'resources', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EquipmentInputSerializer(serializers.Serializer):
    """Serializer for equipment input in booking creation"""
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for creating a new booking"""
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    court_id = serializers.IntegerField()
    equipment = EquipmentInputSerializer(many=True, required=False, allow_empty=True)
    coach_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_date(self, value):
        """Validate that booking date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("Cannot book for past dates")
        return value
    
    def validate(self, data):
        """Validate time constraints"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time")
        return data




class AvailabilityQuerySerializer(serializers.Serializer):
    """Serializer for checking resource availability"""
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class AvailabilityResponseSerializer(serializers.Serializer):
    """Serializer for availability response"""
    courts = CourtSerializer(many=True)
    coaches = CoachSerializer(many=True)
    equipment = serializers.ListField(
        child=serializers.DictField()
    )


class PriceCalculationSerializer(serializers.Serializer):
    """Serializer for price calculation"""
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    court_id = serializers.IntegerField()
    equipment = EquipmentInputSerializer(many=True, required=False, allow_empty=True)
    coach_id = serializers.IntegerField(required=False, allow_null=True)
