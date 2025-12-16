# Badminton Court Booking System - Backend

A complete Django 5 + Django REST Framework backend for managing badminton court bookings with atomic transactions, configuration-driven pricing, and comprehensive resource management.

## Features

✅ **JWT Authentication** - Secure token-based API authentication  
✅ **Atomic Bookings** - All-or-nothing booking with concurrency safety  
✅ **Dynamic Pricing** - Rule-based pricing engine with stacking support  
✅ **Resource Management** - Courts, equipment, and coaches  
✅ **Django Admin** - Full-featured admin dashboard  
✅ **REST APIs** - Complete API for all operations  
✅ **Interactive API Docs** - Swagger UI and ReDoc

## Tech Stack

- **Django 5.1.4** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **djangorestframework-simplejwt 5.3.1** - JWT authentication
- **django-filter 24.3** - API filtering
- **drf-spectacular 0.27.2** - OpenAPI 3.0 schema & Swagger UI
- **SQLite** - Database (development)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Sample Data

```bash
python manage.py populate_sample_data
```

This creates:
- 3 courts (2 indoor, 1 outdoor)
- 3 equipment types (rackets, shuttlecocks, shoes)
- 2 coaches with availability for the next 7 days
- Pricing rules (peak hour, weekend, indoor court)
- Base prices for resources

### 4. Create Superuser (for Admin Access)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

**Important URLs**:
- **Swagger UI (Interactive API Docs)**: http://127.0.0.1:8000/api/docs/
- **ReDoc (Alternative API Docs)**: http://127.0.0.1:8000/api/redoc/
- **Admin Dashboard**: http://127.0.0.1:8000/admin/  
- **API Root**: http://127.0.0.1:8000/

> 💡 **Tip**: Visit Swagger UI for interactive API testing with a user-friendly interface!

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token

### Resources (Read-Only)
- `GET /api/courts/` - List all active courts
- `GET /api/equipment/` - List all equipment
- `GET /api/coaches/` - List all active coaches

### Booking Operations
- `POST /api/availability/` - Check available resources
- `POST /api/price-calculation/` - Calculate booking price
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/` - List user's bookings
- `GET /api/bookings/{id}/` - Get booking details
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `GET /api/bookings/history/` - User booking history

## Example API Usage

### 1. Register User

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login (Get JWT Token)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Check Availability

```bash
curl -X POST http://127.0.0.1:8000/api/availability/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-16",
    "start_time": "10:00",
    "end_time": "11:00"
  }'
```

### 4. Calculate Price

```bash
curl -X POST http://127.0.0.1:8000/api/price-calculation/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-16",
    "start_time": "18:00",
    "end_time": "19:00",
    "court_id": 1,
    "equipment": [{"id": 1, "quantity": 2}],
    "coach_id": 1
  }'
```

### 5. Create Booking

```bash
curl -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-16",
    "start_time": "10:00",
    "end_time": "11:00",
    "court_id": 1,
    "equipment": [{"id": 1, "quantity": 2}],
    "coach_id": 1
  }'
```

## Project Structure

```
backend/
├── authentication/      # User registration and JWT auth
├── resources/          # Courts, equipment, coaches
├── pricing/            # Pricing rules and calculations
├── bookings/           # Booking management
├── backend/            # Django project settings
├── manage.py
└── requirements.txt
```

## Key Features Explained

### Atomic Bookings
Uses Django's `transaction.atomic()` with `select_for_update()` for row-level locking to prevent:
- Double booking of courts
- Overbooking of equipment
- Coach scheduling conflicts
- Race conditions during concurrent requests

### Pricing Engine
Configuration-driven pricing with rule stacking:
- **Base Prices**: Configurable per resource type
- **Pricing Rules**: Peak hour (6 PM-10 PM), weekend, indoor court
- **Rule Stacking**: Multiple rules combine additively (e.g., 20% + 15% = 35%)

### Django Admin
Full CRUD access for:
- Courts and equipment management
- Coach availability scheduling
- Pricing rule configuration
- Booking management (view/cancel)

## Business Logic

### Availability Checking
- Detects time overlaps for courts and coaches
- Tracks equipment quantities across bookings
- Validates coach availability schedules

### Resource Locking
- Uses database-level locks during booking creation
- Ensures atomic all-or-nothing resource allocation
- Prevents race conditions in concurrent scenarios

## Development Notes

- **Database**: SQLite for development; use PostgreSQL for production
- **Timezone**: UTC (configurable in settings.py)
- **Security**: JWT authentication, CSRF protection enabled
- **Code Style**: PEP 8 compliant, comprehensive docstrings

## Testing

Run the included test script:

```bash
python test_booking_flow.py
```

Or test manually via Django shell:

```bash
python manage.py shell
```

## Admin Dashboard Features

Login at http://127.0.0.1:8000/admin/ with superuser credentials

**Manage**:
- Courts: Add/edit courts, toggle active status
- Equipment: Set quantities, track availability
- Coaches: Manage coaches and their availability
- Pricing Rules: Configure and toggle rules
- Bookings: View bookings, bulk cancel

## Future Enhancements

- [ ] Migrate to PostgreSQL for production
- [ ] Add Redis for caching and sessions
- [ ] Implement comprehensive test suite
- [ ] Email notifications for bookings
- [ ] Payment integration
- [ ] Booking history reports

## License

This project is for demonstration purposes.

---

**Built with Django 5 + Django REST Framework**
