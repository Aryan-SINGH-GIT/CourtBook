import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User

# Configuration
BASE_URL = 'http://localhost:8000/api'
USERNAME = 'testuser'
PASSWORD = 'password'

def ensure_user():
    try:
        user = User.objects.get(username=USERNAME)
        user.set_password(PASSWORD)
        user.save()
        print(f"User {USERNAME} updated.")
    except User.DoesNotExist:
        User.objects.create_user(USERNAME, 'test@test.com', PASSWORD)
        print(f"User {USERNAME} created.")

def get_token():
    ensure_user()
    try:
        response = requests.post(f'{BASE_URL}/auth/login/', data={'username': USERNAME, 'password': PASSWORD})
        if response.status_code == 200:
            return response.json()['access']
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def test_pricing():
    token = get_token()
    if not token:
        return

    headers = {'Authorization': f'Bearer {token}'}
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Testing pricing for {today}...")
    
    try:
        response = requests.get(f'{BASE_URL}/daily-matrix/?date={today}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            # print(json.dumps(data, indent=2))
            
            # Check a few slots
            if len(data) > 0:
                court = data[0]
                print(f"Checking Court: {court['name']}")
                
                for slot in court['slots']:
                    time_str = slot['time']
                    price = slot.get('price')
                    
                    # Basic check: Peak is 18:00 - 21:00
                    hour = int(time_str.split(':')[0])
                    is_peak = 18 <= hour < 21
                    
                    print(f"Slot {time_str}: Price {price} | Peak: {is_peak}")
                    
        else:
            print(f"API Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    test_pricing()
