"""
Configuration-driven pricing engine with support for rule stacking.
Calculates booking prices based on base prices and active pricing rules.
"""

from datetime import date, time, datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from pricing.models import PricingRule, BasePrice
from resources.models import Court, Equipment, Coach


class PricingService:
    """Service to calculate prices for bookings based on rules"""
    
    @staticmethod
    def get_base_price(resource_type: str) -> Decimal:
        """Get base price for a resource type"""
        try:
            base_price = BasePrice.objects.get(resource_type=resource_type, is_active=True)
            return base_price.price
        except BasePrice.DoesNotExist:
            # Default prices if not configured
            defaults = {
                'COURT_HOUR': Decimal('50.00'),
                'EQUIPMENT_HOUR': Decimal('10.00'),
                'COACH_HOUR': Decimal('75.00'),
            }
            return defaults.get(resource_type, Decimal('0.00'))
    
    @staticmethod
    def calculate_duration_hours(start_time: time, end_time: time) -> Decimal:
        """Calculate duration in hours between start and end times"""
        start_datetime = datetime.combine(date.today(), start_time)
        end_datetime = datetime.combine(date.today(), end_time)
        duration_seconds = (end_datetime - start_datetime).total_seconds()
        hours = Decimal(str(duration_seconds / 3600))
        return hours
    
    @staticmethod
    def is_peak_hour(start_time: time, end_time: time) -> bool:
        """
        Determine if the booking falls within peak hours.
        Peak hours: 6 PM - 10 PM (18:00 - 22:00)
        """
        peak_start = time(18, 0)
        peak_end = time(21, 0)
        
        # Check if any part of the booking overlaps with peak hours
        return (start_time < peak_end and end_time > peak_start)
    
    @staticmethod
    def is_weekend(booking_date: date) -> bool:
        """Check if the booking is on a weekend (Saturday=5, Sunday=6)"""
        return booking_date.weekday() >= 5
    
    @staticmethod
    def is_indoor_court(court_id: int) -> bool:
        """Check if the court is an indoor court"""
        try:
            court = Court.objects.get(id=court_id)
            return court.court_type == 'INDOOR'
        except Court.DoesNotExist:
            return False
    
    @staticmethod
    def apply_pricing_rules(base_price: Decimal, booking_date: date, start_time: time, end_time: time, court_id: int = None) -> Tuple[Decimal, List[Dict[str, Any]]]:
        """
        Apply all active pricing rules to the base price.
        Rules are stacked additively (percentages add up).
        
        Args:
            base_price: Base price before rules
            booking_date: Date of booking
            start_time: Start time
            end_time: End time
            court_id: Optional court ID for court-specific rules
            
        Returns:
            Tuple of (final_price, list of applied rules)
        """
        applied_rules = []
        total_percentage_increase = Decimal('0')
        total_fixed_increase = Decimal('0')
        
        # Get all active pricing rules
        active_rules = PricingRule.objects.filter(is_active=True)
        
        for rule in active_rules:
            should_apply = False
            
            # Check conditions for each rule type
            if rule.rule_type == 'PEAK_HOUR':
                should_apply = PricingService.is_peak_hour(start_time, end_time)
            elif rule.rule_type == 'WEEKEND':
                should_apply = PricingService.is_weekend(booking_date)
            elif rule.rule_type == 'INDOOR_COURT' and court_id:
                should_apply = PricingService.is_indoor_court(court_id)
            
            if should_apply:
                applied_rules.append({
                    'rule_type': rule.get_rule_type_display(),
                    'value': rule.value,
                    'is_percentage': rule.is_percentage
                })
                
                if rule.is_percentage:
                    total_percentage_increase += rule.value
                else:
                    total_fixed_increase += rule.value
        
        # Calculate final price with stacked rules
        # Apply percentage increases additively (e.g., 20% + 10% = 30% total)
        price_after_percentage = base_price * (Decimal('1') + (total_percentage_increase / Decimal('100')))
        final_price = price_after_percentage + total_fixed_increase
        
        return final_price, applied_rules
    
    @staticmethod
    def calculate_booking_price(
        booking_date: date,
        start_time: time,
        end_time: time,
        court_id: int,
        equipment_list: List[Dict[str, int]] = None,
        coach_id: int = None
    ) -> Dict[str, Any]:
        """
        Calculate total price for a booking with all resources.
        
        Args:
            booking_date: Date of booking
            start_time: Start time
            end_time: End time
            court_id: Court ID
            equipment_list: List of dicts with 'id' and 'quantity'
            coach_id: Optional coach ID
            
        Returns:
            Dict with price breakdown and total
        """
        duration_hours = PricingService.calculate_duration_hours(start_time, end_time)
        
        # Calculate court price
        court_base_price = PricingService.get_base_price('COURT_HOUR')
        court_base_total = court_base_price * duration_hours
        
        court_final_price, applied_rules = PricingService.apply_pricing_rules(
            court_base_total,
            booking_date,
            start_time,
            end_time,
            court_id
        )
        
        breakdown = {
            'duration_hours': float(duration_hours),
            'court': {
                'base_price_per_hour': float(court_base_price),
                'base_total': float(court_base_total),
                'final_price': float(court_final_price),
                'applied_rules': applied_rules
            },
            'equipment': [],
            'coach': None,
            'total_price': float(court_final_price)
        }
        
        # Add equipment costs
        if equipment_list:
            equipment_base_price = PricingService.get_base_price('EQUIPMENT_HOUR')
            for eq in equipment_list:
                try:
                    equipment = Equipment.objects.get(id=eq['id'])
                    quantity = eq.get('quantity', 1)
                    eq_total = equipment_base_price * duration_hours * quantity
                    
                    breakdown['equipment'].append({
                        'id': equipment.id,
                        'name': equipment.name,
                        'quantity': quantity,
                        'price_per_hour': float(equipment_base_price),
                        'total_price': float(eq_total)
                    })
                    
                    breakdown['total_price'] += float(eq_total)
                except Equipment.DoesNotExist:
                    pass
        
        # Add coach cost
        if coach_id:
            try:
                coach = Coach.objects.get(id=coach_id, is_active=True)
                coach_base_price = PricingService.get_base_price('COACH_HOUR')
                coach_total = coach_base_price * duration_hours
                
                breakdown['coach'] = {
                    'id': coach.id,
                    'name': coach.name,
                    'price_per_hour': float(coach_base_price),
                    'total_price': float(coach_total)
                }
                
                breakdown['total_price'] += float(coach_total)
            except Coach.DoesNotExist:
                pass
        
        return breakdown
