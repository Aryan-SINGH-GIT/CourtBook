"""
Management command to populate the database with sample data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resources.models import Court, Equipment, Coach, CoachAvailability
from pricing.models import PricingRule, BasePrice
from datetime import date, time, timedelta


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create base prices
        self.stdout.write('Creating base prices...')
        BasePrice.objects.get_or_create(
            resource_type='COURT_HOUR',
            defaults={'price': 50.00, 'is_active': True}
        )
        BasePrice.objects.get_or_create(
            resource_type='EQUIPMENT_HOUR',
            defaults={'price': 10.00, 'is_active': True}
        )
        BasePrice.objects.get_or_create(
            resource_type='COACH_HOUR',
            defaults={'price': 75.00, 'is_active': True}
        )
        
        # Create pricing rules
        self.stdout.write('Creating pricing rules...')
        PricingRule.objects.get_or_create(
            rule_type='PEAK_HOUR',
            defaults={'value': 20, 'is_percentage': True, 'is_active': True}
        )
        PricingRule.objects.get_or_create(
            rule_type='WEEKEND',
            defaults={'value': 15, 'is_percentage': True, 'is_active': True}
        )
        PricingRule.objects.get_or_create(
            rule_type='INDOOR_COURT',
            defaults={'value': 10, 'is_percentage': True, 'is_active': True}
        )
        
        # Create courts
        self.stdout.write('Creating courts...')
        Court.objects.get_or_create(
            name='Court 1',
            defaults={'court_type': 'INDOOR', 'is_active': True}
        )
        Court.objects.get_or_create(
            name='Court 2',
            defaults={'court_type': 'INDOOR', 'is_active': True}
        )
        Court.objects.get_or_create(
            name='Court 3',
            defaults={'court_type': 'OUTDOOR', 'is_active': True}
        )
        
        # Create equipment
        self.stdout.write('Creating equipment...')
        Equipment.objects.get_or_create(
            name='Badminton Racket',
            defaults={'total_quantity': 10, 'available_quantity': 10}
        )
        Equipment.objects.get_or_create(
            name='Shuttlecock (set of 12)',
            defaults={'total_quantity': 20, 'available_quantity': 20}
        )
        Equipment.objects.get_or_create(
            name='Sports Shoes',
            defaults={'total_quantity': 8, 'available_quantity': 8}
        )
        
        # Create coaches
        self.stdout.write('Creating coaches...')
        coach1, _ = Coach.objects.get_or_create(
            name='Rajesh Sharma',
            defaults={'is_active': True}
        )
        coach2, _ = Coach.objects.get_or_create(
            name='Priya Kumar',
            defaults={'is_active': True}
        )
        coach3, _ = Coach.objects.get_or_create(
            name='Amit Mehta',
            defaults={'is_active': True}
        )
        
        # Create coach availability for the next 7 days
        self.stdout.write('Creating coach availability...')
        today = date.today()
        for i in range(7):
            current_date = today + timedelta(days=i)
            
            # Rajesh available mornings 8 AM - 12 PM
            CoachAvailability.objects.get_or_create(
                coach=coach1,
                date=current_date,
                start_time=time(8, 0),
                end_time=time(12, 0)
            )
            
            # Priya available afternoons 1 PM - 5 PM
            CoachAvailability.objects.get_or_create(
                coach=coach2,
                date=current_date,
                start_time=time(13, 0),
                end_time=time(17, 0)
            )
            
            # Amit available evenings 4 PM - 9 PM
            CoachAvailability.objects.get_or_create(
                coach=coach3,
                date=current_date,
                start_time=time(16, 0),
                end_time=time(21, 0)
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('')
        self.stdout.write('Summary:')
        self.stdout.write(f'  - Base Prices: {BasePrice.objects.count()}')
        self.stdout.write(f'  - Pricing Rules: {PricingRule.objects.count()}')
        self.stdout.write(f'  - Courts: {Court.objects.count()}')
        self.stdout.write(f'  - Equipment: {Equipment.objects.count()}')
        self.stdout.write(f'  - Coaches: {Coach.objects.count()}')
        self.stdout.write(f'  - Coach Availabilities: {CoachAvailability.objects.count()}')
