import os
import sys
import django
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from resources.models import Court, Coach, Equipment
from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    print("--- Populating Database ---")

    # 1. Create Courts
    print("\nCreating Courts...")
    courts_data = [
        {'name': 'Court 1', 'court_type': 'INDOOR'},
        {'name': 'Court 2', 'court_type': 'INDOOR'},
        {'name': 'Court 3', 'court_type': 'OUTDOOR'},
        {'name': 'Court 4', 'court_type': 'OUTDOOR'},
    ]
    
    for c_data in courts_data:
        court, created = Court.objects.get_or_create(name=c_data['name'], defaults=c_data)
        if created:
            print(f"  Created: {court}")
        else:
            print(f"  Exists: {court}")

    # 2. Create Coaches
    print("\nCreating Coaches...")
    coaches_data = [
        {'name': 'John Doe'},
        {'name': 'Jane Smith'},
        {'name': 'Mike Johnson'},
    ]
    
    for c_data in coaches_data:
        coach, created = Coach.objects.get_or_create(name=c_data['name'], defaults=c_data)
        if created:
            print(f"  Created: {coach}")
        else:
            print(f"  Exists: {coach}")

    # 3. Create Equipment
    print("\nCreating Equipment...")
    equipment_data = [
        {'name': 'Yonex Racket', 'total_quantity': 20, 'available_quantity': 20},
        {'name': 'Professional Racket', 'total_quantity': 10, 'available_quantity': 10},
        {'name': 'Shuttlecock Box', 'total_quantity': 50, 'available_quantity': 50},
        {'name': 'Badminton Shoes (Size 9)', 'total_quantity': 5, 'available_quantity': 5},
        {'name': 'Badminton Shoes (Size 10)', 'total_quantity': 5, 'available_quantity': 5},
    ]
    
    for e_data in equipment_data:
        equipment, created = Equipment.objects.get_or_create(name=e_data['name'], defaults=e_data)
        if created:
            print(f"  Created: {equipment}")
        else:
            print(f"  Exists: {equipment}")

    # 4. Test User
    print("\nCreating Test User...")
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        print(f"  Created user: {user.username}")
    else:
        print("  User 'testuser' already exists")

    print("\nDatabase populated successfully!")

if __name__ == '__main__':
    run()
