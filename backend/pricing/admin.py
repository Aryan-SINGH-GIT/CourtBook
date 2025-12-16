"""
Django Admin configuration for pricing app
"""

from django.contrib import admin
from pricing.models import PricingRule, BasePrice


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """Admin interface for Pricing Rules"""
    list_display = ('rule_type', 'value', 'is_percentage', 'is_active', 'updated_at')
    list_filter = ('is_active', 'is_percentage', 'rule_type')
    list_editable = ('is_active',)
    ordering = ('rule_type',)


@admin.register(BasePrice)
class BasePriceAdmin(admin.ModelAdmin):
    """Admin interface for Base Prices"""
    list_display = ('resource_type', 'price', 'is_active', 'updated_at')
    list_filter = ('is_active', 'resource_type')
    list_editable = ('price', 'is_active')
    ordering = ('resource_type',)
