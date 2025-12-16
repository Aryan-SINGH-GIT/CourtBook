
import os
import sys
import django
from decimal import Decimal

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from pricing.models import PricingRule, BasePrice

def setup_rules():
    print("Setting up pricing rules...")
    
    # 1. Base Prices
    print("\nSetting up Base Prices...")
    base_prices = [
        {'resource_type': 'COURT_HOUR', 'price': Decimal('200.00')},
        {'resource_type': 'EQUIPMENT_HOUR', 'price': Decimal('100.00')},
        {'resource_type': 'COACH_HOUR', 'price': Decimal('500.00')},
    ]
    
    for bp_data in base_prices:
        bp, created = BasePrice.objects.update_or_create(
            resource_type=bp_data['resource_type'],
            defaults={'price': bp_data['price'], 'is_active': True}
        )
        status = "Created" if created else "Updated"
        print(f"  {status}: {bp}")

    # 2. Pricing Rules
    print("\nSetting up Pricing Rules...")
    rules = [
        {
            'rule_type': 'PEAK_HOUR',
            'value': Decimal('10.00'),
            'is_percentage': True,
            'description': 'Peak Hour Surcharge (+10%)'
        },
        {
            'rule_type': 'WEEKEND',
            'value': Decimal('15.00'),
            'is_percentage': True,
            'description': 'Weekend Surcharge (+15%)'
        },
        {
            'rule_type': 'INDOOR_COURT',
            'value': Decimal('5.00'),
            'is_percentage': True,
            'description': 'Indoor Court Premium (+5%)'
        }
    ]
    
    for rule_data in rules:
        rule, created = PricingRule.objects.update_or_create(
            rule_type=rule_data['rule_type'],
            defaults={
                'value': rule_data['value'],
                'is_percentage': rule_data['is_percentage'],
                'description': rule_data['description'],
                'is_active': True
            }
        )
        status = "Created" if created else "Updated"
        print(f"  {status} rule: {rule_data['description']}")

if __name__ == '__main__':
    setup_rules()
