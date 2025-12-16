import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import date
from resources.models import Coach, CoachAvailability

from datetime import date, time, datetime
from resources.models import Coach, CoachAvailability
from resources.services.availability_service import AvailabilityService

def run():
    print(f"Checking coaches for today: {date.today()}")
    
    # Test time slot: 10:00 to 11:00 (Should be within default 6-22 range)
    start_time = time(10, 0)
    end_time = time(11, 0)
    
    print(f"Testing availability for slot: {start_time} - {end_time}")
    
    available_coaches = AvailabilityService.get_available_coaches(date.today(), start_time, end_time)
    print(f"Number of available coaches returned by service: {len(available_coaches)}")
    
    all_active = Coach.objects.filter(is_active=True)
    print(f"Total active coaches in DB: {all_active.count()}")
    
    for coach in all_active:
        is_available = AvailabilityService.check_coach_availability(coach.id, date.today(), start_time, end_time)
        status = "AVAILABLE" if is_available else "UNAVAILABLE"
        print(f"Coach: {coach.name} -> {status}")
        
        # Check specific records just for info
        has_records = CoachAvailability.objects.filter(coach=coach, date=date.today()).exists()
        print(f"  (Has specific records today: {has_records})")

if __name__ == '__main__':
    run()
