"""
Atomic booking service with transaction handling and concurrency safety.
Ensures all-or-nothing booking of courts, equipment, and coaches.
"""

from datetime import date, time
from decimal import Decimal
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from bookings.models import Booking, BookingResource
from resources.models import Court, Equipment, Coach
from resources.services.availability_service import AvailabilityService
from pricing.services.pricing_service import PricingService


class BookingService:
    """Service to handle booking creation with atomic transactions"""
    
    @staticmethod
    @transaction.atomic
    def create_booking(
        user: User,
        booking_date: date,
        start_time: time,
        end_time: time,
        court_id: int,
        equipment_list: List[Dict[str, int]] = None,
        coach_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new booking with all resources atomically.
        Uses database-level locking to prevent race conditions.
        
        Args:
            user: User making the booking
            booking_date: Date of booking
            start_time: Start time  
            end_time: End time
            court_id: ID of court to book
            equipment_list: List of dicts with 'id' and 'quantity'
            coach_id: Optional coach ID
            
        Returns:
            Dict with booking details or error
            
        Raises:
            ValidationError: If any validation fails or resources unavailable
        """
        # Validate basic time constraints
        if start_time >= end_time:
            raise ValidationError("Start time must be before end time")
        
        if booking_date < date.today():
            raise ValidationError("Cannot book for past dates")
        
        # Lock resources for the duration of the transaction
        # This prevents race conditions when multiple requests come simultaneously
        
        # Check court availability with SELECT FOR UPDATE (row-level lock)
        try:
            court = Court.objects.select_for_update().get(id=court_id, is_active=True)
        except Court.DoesNotExist:
            raise ValidationError(f"Court with ID {court_id} not found or inactive")
        
        if not AvailabilityService.check_court_availability(
            court_id, booking_date, start_time, end_time
        ):
            raise ValidationError(f"Court {court.name} is not available for the selected time slot")
        
        # Check equipment availability
        equipment_items = []
        if equipment_list:
            for eq in equipment_list:
                eq_id = eq.get('id')
                quantity = eq.get('quantity', 1)
                
                try:
                    equipment = Equipment.objects.select_for_update().get(id=eq_id)
                except Equipment.DoesNotExist:
                    raise ValidationError(f"Equipment with ID {eq_id} not found")
                
                if not AvailabilityService.check_equipment_availability(
                    eq_id, quantity, booking_date, start_time, end_time
                ):
                    raise ValidationError(
                        f"Equipment '{equipment.name}' not available in requested quantity ({quantity})"
                    )
                
                equipment_items.append({'equipment': equipment, 'quantity': quantity})
        
        # Check coach availability
        coach = None
        if coach_id:
            try:
                coach = Coach.objects.select_for_update().get(id=coach_id, is_active=True)
            except Coach.DoesNotExist:
                raise ValidationError(f"Coach with ID {coach_id} not found or inactive")
            
            if not AvailabilityService.check_coach_availability(
                coach_id, booking_date, start_time, end_time
            ):
                raise ValidationError(f"Coach {coach.name} is not available for the selected time slot")
        
        # Calculate total price
        equipment_for_pricing = [
            {'id': eq['equipment'].id, 'quantity': eq['quantity']}
            for eq in equipment_items
        ] if equipment_items else None
        
        price_breakdown = PricingService.calculate_booking_price(
            booking_date,
            start_time,
            end_time,
            court_id,
            equipment_for_pricing,
            coach_id
        )
        
        total_price = Decimal(str(price_breakdown['total_price']))
        
        # Create the booking
        booking = Booking.objects.create(
            user=user,
            date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price,
            status='CONFIRMED'
        )
        
        # Create booking resources
        # Court
        BookingResource.objects.create(
            booking=booking,
            resource_type='COURT',
            resource_id=court_id,
            quantity=1
        )
        
        # Equipment
        for eq_item in equipment_items:
            BookingResource.objects.create(
                booking=booking,
                resource_type='EQUIPMENT',
                resource_id=eq_item['equipment'].id,
                quantity=eq_item['quantity']
            )
        
        # Coach
        if coach:
            BookingResource.objects.create(
                booking=booking,
                resource_type='COACH',
                resource_id=coach_id,
                quantity=1
            )
        
        return {
            'success': True,
            'booking_id': booking.id,
            'booking': booking,
            'price_breakdown': price_breakdown,
            'message': 'Booking created successfully'
        }
    
    @staticmethod
    @transaction.atomic
    def cancel_booking(booking_id: int, user: User) -> Dict[str, Any]:
        """
        Cancel a booking and release all resources.
        
        Args:
            booking_id: ID of booking to cancel
            user: User requesting cancellation
            
        Returns:
            Dict with success status and message
            
        Raises:
            ValidationError: If booking not found or cannot be cancelled
        """
        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)
        except Booking.DoesNotExist:
            raise ValidationError(f"Booking with ID {booking_id} not found")
        
        # Verify ownership (or admin)
        if booking.user != user and not user.is_staff:
            raise ValidationError("You do not have permission to cancel this booking")
        
        # Check if already cancelled
        if booking.status == 'CANCELLED':
            raise ValidationError("This booking is already cancelled")
        
        # Check if booking is in the past
        from django.utils import timezone
        import datetime
        
        # Combine date and time to make a datetime object
        booking_datetime = datetime.datetime.combine(booking.date, booking.start_time)
        
        # Make it timezone aware if it's naive (assuming server timezone, usually UTC in Django)
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)
            
        if booking_datetime < timezone.now():
            raise ValidationError("Cannot cancel a booking that has already occurred")
        
        # Update booking status
        booking.status = 'CANCELLED'
        booking.save()
        
        return {
            'success': True,
            'message': f'Booking #{booking_id} cancelled successfully'
        }
    
    @staticmethod
    def get_user_bookings(user: User, status: str = None) -> List[Booking]:
        """
        Get all bookings for a user, optionally filtered by status.
        
        Args:
            user: User whose bookings to retrieve
            status: Optional status filter ('CONFIRMED' or 'CANCELLED')
            
        Returns:
            QuerySet of bookings
        """
        bookings = Booking.objects.filter(user=user).select_related('user')
        
        if status:
            bookings = bookings.filter(status=status)
        
        return bookings.prefetch_related('resources')
