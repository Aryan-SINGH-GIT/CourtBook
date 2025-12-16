"""
Availability checking service for courts, coaches, and equipment.
Prevents double booking and ensures resource availability.
"""

from datetime import date, time
from typing import List, Dict, Any
from django.db.models import Q
from resources.models import Court, Equipment, Coach, CoachAvailability
from bookings.models import Booking, BookingResource


class AvailabilityService:
    """Service to check availability of courts, coaches, and equipment"""
    
    @staticmethod
    def check_court_availability(court_id: int, booking_date: date, start_time: time, end_time: time, exclude_booking_id: int = None) -> bool:
        """
        Check if a court is available for the given time slot.
        
        Args:
            court_id: ID of the court to check
            booking_date: Date of the booking
            start_time: Start time of the booking
            end_time: End time of the booking
            exclude_booking_id: Optional booking ID to exclude (for updates)
            
        Returns:
            True if available, False otherwise
        """
        try:
            court = Court.objects.get(id=court_id, is_active=True)
        except Court.DoesNotExist:
            return False
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            date=booking_date,
            status='CONFIRMED',
            resources__resource_type='COURT',
            resources__resource_id=court_id
        ).filter(
            # Time overlap condition: new booking overlaps if:
            # (start_time < existing_end AND end_time > existing_start)
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )
        
        if exclude_booking_id:
            overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking_id)
        
        return not overlapping_bookings.exists()
    
    @staticmethod
    def check_coach_availability(coach_id: int, booking_date: date, start_time: time, end_time: time, exclude_booking_id: int = None) -> bool:
        """
        Check if a coach is available for the given time slot.
        First checks coach's availability schedule (defaults to 06:00-22:00 if not set), 
        then checks for conflicts.
        """
        try:
            coach = Coach.objects.get(id=coach_id, is_active=True)
        except Coach.DoesNotExist:
            return False
        
        # Check if coach has specific availability records for this time slot
        specific_availability = CoachAvailability.objects.filter(
            coach_id=coach_id,
            date=booking_date
        )
        
        if specific_availability.exists():
            # If specific records exist, the slot MUST fall within one of them
            is_within_schedule = specific_availability.filter(
                start_time__lte=start_time,
                end_time__gte=end_time
            ).exists()
            
            if not is_within_schedule:
                return False
        else:
            # Default availability: 06:00 to 22:00
            default_start = time(6, 0)
            default_end = time(22, 0)
            
            if not (start_time >= default_start and end_time <= default_end):
                return False
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            date=booking_date,
            status='CONFIRMED',
            resources__resource_type='COACH',
            resources__resource_id=coach_id
        ).filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )
        
        if exclude_booking_id:
            overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking_id)
        
        return not overlapping_bookings.exists()

    @staticmethod
    def check_equipment_availability(equipment_id: int, quantity: int, booking_date: date, start_time: time, end_time: time, exclude_booking_id: int = None) -> bool:
        """
        Check if sufficient quantity of equipment is available.
        
        Args:
            equipment_id: ID of the equipment to check
            quantity: Quantity needed
            booking_date: Date of the booking
            start_time: Start time of the booking
            end_time: End time of the booking
            exclude_booking_id: Optional booking ID to exclude (for updates)
            
        Returns:
            True if available, False otherwise
        """
        try:
            equipment = Equipment.objects.get(id=equipment_id)
        except Equipment.DoesNotExist:
            return False
        
        # Check if requested quantity is available at all
        if equipment.available_quantity < quantity:
            return False
        
        # Calculate how much is already booked for overlapping time slots
        overlapping_bookings = Booking.objects.filter(
            date=booking_date,
            status='CONFIRMED',
            resources__resource_type='EQUIPMENT',
            resources__resource_id=equipment_id
        ).filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )
        
        if exclude_booking_id:
            overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking_id)
        
        # Sum up the quantities already booked
        booked_quantity = sum(
            br.quantity for booking in overlapping_bookings
            for br in booking.resources.filter(resource_type='EQUIPMENT', resource_id=equipment_id)
        )
        
        available_for_slot = equipment.total_quantity - booked_quantity
        
        return available_for_slot >= quantity
    
    @staticmethod
    def get_available_courts(booking_date: date, start_time: time, end_time: time) -> List[Court]:
        """Get list of courts available for a given time slot"""
        all_courts = Court.objects.filter(is_active=True)
        available_courts = []
        
        for court in all_courts:
            if AvailabilityService.check_court_availability(court.id, booking_date, start_time, end_time):
                available_courts.append(court)
        
        return available_courts
    
    @staticmethod
    def get_available_coaches(booking_date: date, start_time: time, end_time: time) -> List[Coach]:
        """Get list of coaches available for a given time slot"""
        # Check all active coaches
        all_active_coaches = Coach.objects.filter(is_active=True)
        
        available_coaches = []
        for coach in all_active_coaches:
            if AvailabilityService.check_coach_availability(coach.id, booking_date, start_time, end_time):
                available_coaches.append(coach)
        
        return available_coaches
    
    @staticmethod
    def get_equipment_availability(booking_date: date, start_time: time, end_time: time) -> List[Dict[str, Any]]:
        """
        Get equipment availability with quantities for a given time slot.
        
        Returns:
            List of dicts with equipment details and available quantity
        """
        all_equipment = Equipment.objects.all()
        equipment_availability = []
        
        for equipment in all_equipment:
            # Calculate available quantity for this time slot
            overlapping_bookings = Booking.objects.filter(
                date=booking_date,
                status='CONFIRMED',
                resources__resource_type='EQUIPMENT',
                resources__resource_id=equipment.id
            ).filter(
                Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
            )
            
            booked_quantity = sum(
                br.quantity for booking in overlapping_bookings
                for br in booking.resources.filter(resource_type='EQUIPMENT', resource_id=equipment.id)
            )
            
            available_quantity = equipment.total_quantity - booked_quantity
            
            equipment_availability.append({
                'equipment': equipment,
                'available_quantity': available_quantity,
                'total_quantity': equipment.total_quantity
            })
        
        return equipment_availability
