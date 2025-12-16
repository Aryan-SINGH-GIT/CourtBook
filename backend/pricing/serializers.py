from rest_framework import serializers
from .models import BasePrice, PricingRule

class BasePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasePrice
        fields = ['resource_type', 'price']

class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingRule
        fields = ['rule_type', 'value', 'is_percentage', 'description']
