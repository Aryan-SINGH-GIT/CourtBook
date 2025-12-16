
import os
import django
import sys
import json
from datetime import date, time, timedelta

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from bookings.views import DailyAvailabilityView, AddonAvailabilityView, BookingViewSet, CourtViewSet, EquipmentViewSet
from django.contrib.auth.models import User
from resources.models import Court

def verify_apis():
    print("="*60)
    print("VERIFYING ACTIVE APIs")
    print("="*60)
    
    # Setup
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
    factory = APIRequestFactory()
    today = date.today().isoformat()
    
    # 1. Daily Matrix API
    print("\n[1] Testing Daily Matrix API...")
    request = factory.get(f'/api/bookings/daily-matrix/?date={today}')
    force_authenticate(request, user=user)
    view = DailyAvailabilityView.as_view()
    response = view(request)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"SUCCESS. Found {len(response.data)} courts.")
    else:
        print("FAILED.")
        print(response.data)

    # 2. Addon Availability API
    print("\n[2] Testing Addon Availability API...")
    request = factory.get(f'/api/bookings/addon-availability/?date={today}&start_time=10:00:00&end_time=11:00:00')
    force_authenticate(request, user=user)
    view = AddonAvailabilityView.as_view()
    response = view(request)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"SUCCESS. found {len(response.data.get('coaches', []))} coaches, {len(response.data.get('equipment', []))} equipment types.")
    else:
        print("FAILED.")
        print(response.data)
        
    # 3. Resources API (Courts)
    print("\n[3] Testing Resources API (Courts)...")
    request = factory.get('/api/courts/')
    force_authenticate(request, user=user)
    view = CourtViewSet.as_view({'get': 'list'})
    response = view(request)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"SUCCESS. Found {len(response.data)} courts.")
    else:
        print("FAILED.")

    # 4. Booking Create API
    print("\n[4] Testing Booking Create API...")
    court = Court.objects.first()
    booking_data = {
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "start_time": "14:00",
        "end_time": "15:00",
        "court_id": court.id,
        "equipment": [],
        "coach_id": None
    }
    request = factory.post('/api/bookings/', booking_data, format='json')
    force_authenticate(request, user=user)
    view = BookingViewSet.as_view({'post': 'create'})
    try:
        response = view(request)
        print(f"Status: {response.status_code}")
        booking_id = None
        if response.status_code == 201:
            booking_id = response.data['id']
            print(f"SUCCESS. Created Booking ID: {booking_id}")
        else:
            print("FAILED.")
            print(response.data)
    except Exception as e:
        print(f"EXCEPTION: {e}")

    # 5. Booking Cancel API
    if booking_id:
        print("\n[5] Testing Booking Cancel API...")
        request = factory.post(f'/api/bookings/{booking_id}/cancel/')
        force_authenticate(request, user=user)
        view = BookingViewSet.as_view({'post': 'cancel'})
        response = view(request, pk=booking_id)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS. Booking Cancelled.")
        else:
            print("FAILED.")
            print(response.data)

if __name__ == '__main__':
    verify_apis()
