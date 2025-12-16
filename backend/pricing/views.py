from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import BasePrice, PricingRule
from .serializers import BasePriceSerializer, PricingRuleSerializer

class PublicPricingView(APIView):
    """
    Public endpoint to get current pricing configuration (Base Prices and Rules).
    Used by the frontend Pricing page.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        base_prices = BasePrice.objects.filter(is_active=True)
        rules = PricingRule.objects.filter(is_active=True)
        
        return Response({
            'base_prices': BasePriceSerializer(base_prices, many=True).data,
            'rules': PricingRuleSerializer(rules, many=True).data
        })
