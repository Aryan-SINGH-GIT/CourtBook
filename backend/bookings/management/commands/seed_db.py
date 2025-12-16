from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from resources.models import Court, Coach, Equipment
from pricing.models import PricingRule, BasePrice
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write("--- Seeding Database ---")

        # 1. Base Prices
        self.stdout.write("\nSetting up Base Prices...")
        base_prices = [
            {'resource_type': 'COURT_HOUR', 'price': Decimal('400.00')},
            {'resource_type': 'EQUIPMENT_HOUR', 'price': Decimal('100.00')},
            {'resource_type': 'COACH_HOUR', 'price': Decimal('500.00')},
        ]
        
        for bp_data in base_prices:
            bp, created = BasePrice.objects.update_or_create(
                resource_type=bp_data['resource_type'],
                defaults={'price': bp_data['price'], 'is_active': True}
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {bp}")

        # 2. Pricing Rules
        self.stdout.write("\nSetting up Pricing Rules...")
        rules = [
            {'rule_type': 'PEAK_HOUR', 'value': Decimal('10.00'), 'is_percentage': True, 'description': 'Peak Hour Surcharge (+10%)'},
            {'rule_type': 'WEEKEND', 'value': Decimal('15.00'), 'is_percentage': True, 'description': 'Weekend Surcharge (+15%)'},
            {'rule_type': 'INDOOR_COURT', 'value': Decimal('5.00'), 'is_percentage': True, 'description': 'Indoor Court Premium (+5%)'}
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
            self.stdout.write(f"  {status} rule: {rule_data['description']}")

        # 3. Courts
        self.stdout.write("\nCreating Courts...")
        courts_data = [
            {'name': 'Court 1', 'court_type': 'INDOOR'},
            {'name': 'Court 2', 'court_type': 'INDOOR'},
            {'name': 'Court 3', 'court_type': 'OUTDOOR'},
            {'name': 'Court 4', 'court_type': 'OUTDOOR'},
        ]
        for c_data in courts_data:
            court, created = Court.objects.get_or_create(name=c_data['name'], defaults=c_data)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {court}")

        # 4. Coaches
        self.stdout.write("\nCreating Coaches...")
        coaches_data = [{'name': 'Amit Mehta'}, {'name': 'Priya Kumar'}, {'name': 'Rajesh Sharma'}]
        for c_data in coaches_data:
            coach, created = Coach.objects.get_or_create(name=c_data['name'], defaults=c_data)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {coach}")

        # 5. Equipment
        self.stdout.write("\nCreating Equipment...")
        equipment_data = [
            {'name': 'Badminton Racket', 'total_quantity': 10, 'available_quantity': 10},
            {'name': 'Shuttlecock Box', 'total_quantity': 50, 'available_quantity': 50},
            {'name': 'Badminton Shoes', 'total_quantity': 5, 'available_quantity': 5},
        ]
        for e_data in equipment_data:
            equipment, created = Equipment.objects.get_or_create(name=e_data['name'], defaults=e_data)
            self.stdout.write(f"  {'Created' if created else 'Exists'}: {equipment}")

        # 6. Test User
        self.stdout.write("\nCreating Test User...")
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user('testuser', 'test@example.com', 'password123')
            self.stdout.write(f"  Created user: {user.username}")
        else:
            self.stdout.write("  User 'testuser' already exists")

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
