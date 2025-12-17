# Badminton Court Booking System

## Setup Instructions

### Backend Setup
1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Configuration**:
   Create a `.env` file in the `backend/` directory with your database settings and `SECRET_KEY`.
5. **Database Migration**:
   ```bash
   python manage.py migrate
   ```
6. **Start Server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Start Development Server**:
   ```bash
   npm run dev
   ```
4. **Access Application**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Assumptions Made

1. **Authentication**: Users must register and log in to make bookings. We assume a standard JWT-based flow is sufficient for security.
2. **User Roles**: The current system primarily distinguishes between regular authenticated users and Staff/Admins. Staff have broader access to cancellations and overrides.
3. **Time Slots**: Bookings are made in configurable time blocks. We assume typical operating hours (e.g., 6 AM to 10 PM) for validity checks.
4. **Currency**: All prices are calculated and displayed in the system's default currency (assumed USD or local currency unit), stored as decimals.
5. **Concurrency**: We assume high concurrent usage is possible, hence the need for strict database-level locking during booking creation.

---

## Seed Data

To populate the database with initial data for courts, equipment, coaches, and pricing rules, run the provided utility scripts from the `backend/` directory:

1. **Populate Resources (Courts, Coaches, Equipment, Test User)**:
   ```bash
   python scripts/populate_db.py
   ```
   *Creates 4 courts, 3 coaches, various equipment items, and a test user (`testuser`/`password123`).*

2. **Setup Pricing Rules**:
   ```bash
   python scripts/setup_pricing_rules.py
   ```
   *Configures Base Prices (Court $200, Coach $500, Equipment $100) and Pricing Rules (Peak Hour +10%, Weekend +15%, Indoor +5%).*

---

## Database Design & Pricing Engine Approach

### Database Design

The database schema is designed for flexibility, data integrity, and atomicity. The core of the system is the `Booking` model, which acts as the transactional root. Instead of creating separate tables for every resource type linked to a booking (e.g., `BookingCourt`, `BookingCoach`), we utilized a **polymorphic-like pattern** with the `BookingResource` model. This "junction table" genericizes resource management, allowing a single booking to be associated with multiple resource types (Court, Equipment, Coach) through `resource_type` and `resource_id` fields.

This normalized design allows for:
*   **Extensibility**: Adding a new resource type (e.g., "Locker") requires minimal schema changes—just an update to the `RESOURCE_TYPE_CHOICES` enum and a new reference model.
*   **Atomicity**: The `BookingService` wraps the creation of the `Booking` record and all its `BookingResource` entries in a single atomic transaction (`@transaction.atomic`). We leverage **`select_for_update()`** to lock the specific rows of the Court, Coach, and Equipment tables during the validation and creation phase. This strictly prevents race conditions where two users might try to book the last available court or racket simultaneously; one transaction will succeed, and the other will fail safely.

Pricing configurations are decoupled from the resources themselves. `BasePrice` and `PricingRule` models allow admins to adjust rates without altering code or resource table structures, supporting a data-driven configuration approach.

### Pricing Engine Approach

The pricing logic is encapsulated in the separate `PricingService`, keeping business rules distinct from data models and view logic. The engine uses a **stackable rule-based system**.

1.  **Base Price Retrieval**: The system first fetches the specific `BasePrice` for the resource type (e.g., "Court per Hour").
2.  **Duration Calculation**: It accurately parses the start and end times to determine the billable duration in hours.
3.  **Dynamic Rule Application**: The engine queries all active `PricingRule` entries. It iterates through them and evaluates their applicability based on the booking context:
    *   **Time-based**: Checks if the slot falls within defined "Peak Hours" (e.g., 18:00–22:00).
    *   **Date-based**: Checks if the booking date is a weekend using robust date utilities.
    *   **Attribute-based**: Checks if the specific resource has premium attributes (e.g., "Indoor" courts).
4.  **Additive Calculation**: Instead of complex compounding, we adopted a transparent additive model for percentages. All applicable percentage modifiers (e.g., +10% Peak, +5% Indoor) are summed first (Total +15%) and then applied to the base price. Fixed-fee modifiers are added subsequently. This ensures price transparency and predictability for the user.

This "Decorator-style" logic allows for highly dynamic pricing updates (e.g., "Surge Pricing") simply by adding active rows to the `PricingRule` table.

---

## ⚡ Atomicity & Concurrency Handling

A critical requirement for any booking system is preventing double bookings. This system enforces strict **Atomicity** and **Concurrency Control**:

*   **Atomic Transactions**: The `BookingService` wraps the entire booking process (Booking creation + Resource associations) in a single atomic block using `@transaction.atomic`. If any step fails (e.g., equipment insufficient), the entire operation rolls back.
*   **Row-Level Locking**: We utilize `select_for_update()` to lock the specific rows for the Court, Coach, and Equipment being booked.
    *   *Scenario*: If User A and User B try to book "Court 1" at 10:00 AM simultaneously, the database locks the row for the first requester. The second requester waits (or fails immediately depending on config) until the first transaction commits. This guarantees data integrity at the database level, not just the application level.

---

## 📸 Screenshots


### Booking Dashboard
<img width="1334" height="685" alt="image" src="https://github.com/user-attachments/assets/48daa009-4097-4a36-ac7c-be3350671c72" />


### Booking Flow
<img width="1416" height="728" alt="image" src="https://github.com/user-attachments/assets/f056ea32-b466-41e0-b66d-a5285d9619e4" />


### Pricing & Checkout
<img width="1405" height="700" alt="image" src="https://github.com/user-attachments/assets/fbd4cf3d-8462-4f75-b39b-25e05527a8ce" />


### Landing Page
<img width="1439" height="814" alt="image" src="https://github.com/user-attachments/assets/b11a98ec-6fb4-471e-9f73-196f8493586e" />

---

## 🛡️ Admin Panel Capabilities

The application includes a fully configured Django Admin interface (`/admin/`) for backend management.

### 1. Booking Management
*   **Overview**: View all user bookings with advanced filtering (Date, Status).
*   **Bulk Actions**: "Cancel selected bookings" action allows admins to safely cancel multiple bookings at once (triggering atomic stock return).
*   **Details**: View associated resources (Courts, Equipment) directly within the booking detail view.

### 2. Resource Management
*   **Courts**: fast toggle for `is_active` status (e.g., for maintenance).
*   **Equipment**: Monitor `total_quantity` vs `available_quantity`.
*   **Coaches**: Manage profiles and specific `CoachAvailability` slots.

### 3. Dynamic Pricing Control
*   **Base Prices**: Adjust the base hourly rate for Courts, Coaches, or Equipment on the fly.
*   **Pricing Rules**: Enable/Disable rules (Peak Hour, Weekend, Indoor) or adjust their percentage values without deploying new code.
