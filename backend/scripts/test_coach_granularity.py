import os
import sys
import django
from datetime import date, time, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from resources.models import Coach
from bookings.models import Booking, BookingResource
from resources.services.availability_service import AvailabilityService
from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    print(f"--- Testing Coach Availability Granularity ---")
    today = date.today()
    print(f"Date: {today}")

    # 1. Get a coach and user
    coach = Coach.objects.filter(is_active=True).first()
    if not coach:
        print("ERROR: No active coach found.")
        return
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        # fallback if no superuser
        user = User.objects.first()
    if not user:
         # Create dummy user if absolutely none
         user = User.objects.create_user(username='test_granularity_user', password='password')

    
    print(f"Using Coach: {coach.name} (ID: {coach.id})")
    print(f"Using User: {user.username}")

    # 2. Define slots
    slot1_start = time(10, 0)
    slot1_end = time(11, 0) # 10-11
    
    slot2_start = time(11, 0)
    slot2_end = time(12, 0) # 11-12

    # Cleanup existing bookings for this test slot to ensure clean state
    existing = Booking.objects.filter(
        date=today, 
        resources__resource_type='COACH', 
        resources__resource_id=coach.id,
        start_time=slot1_start
    )
    if existing.exists():
        print("Cleaning up existing conflicting bookings...")
        existing.delete()

    # 3. Verify Initial State (Should be Available)
    avail = AvailabilityService.check_coach_availability(coach.id, today, slot1_start, slot1_end)
    print(f"Initial Check (10-11): {'AVAILABLE' if avail else 'UNAVAILABLE'} (Expected: AVAILABLE)")

    # 4. Create Booking for Slot 1 (10-11)
    print("Creating booking for 10:00 - 11:00...")
    booking = Booking.objects.create(
        user=user,
        date=today,
        start_time=slot1_start,
        end_time=slot1_end,
        total_price=500,
        status='CONFIRMED'
    )
    BookingResource.objects.create(
        booking=booking,
        resource_type='COACH',
        resource_id=coach.id,
        quantity=1
    )

    # 5. Check Slot 1 (Should be UNAVAILABLE)
    avail1 = AvailabilityService.check_coach_availability(coach.id, today, slot1_start, slot1_end)
    print(f"Check Slot 1 (10-11) after booking: {'AVAILABLE' if avail1 else 'UNAVAILABLE'} (Expected: UNAVAILABLE)")

    # 6. Check Slot 2 (Should be AVAILABLE)
    avail2 = AvailabilityService.check_coach_availability(coach.id, today, slot2_start, slot2_end)
    print(f"Check Slot 2 (11-12) after booking: {'AVAILABLE' if avail2 else 'UNAVAILABLE'} (Expected: AVAILABLE)")

    # 7. Cleanup
    print("Cleaning up test booking...")
    booking.delete()
    
    if not avail1 and avail2:
        print("\nSUCCESS: Granularity confirmed. Coach is busy only during booked slot.")
    else:
        print("\nFAILURE: Availability logic incorrect.")

if __name__ == '__main__':
    run()
