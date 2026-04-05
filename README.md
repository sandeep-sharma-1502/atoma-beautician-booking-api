# Atoma Backend – Cuatro Labs Pvt Ltd Assessment

This repository contains the production-ready FastAPI backend for **Atoma**, a platform connecting users with professional beauticians for home services. It was built specifically as a submission for the **Cuatro Labs Pvt Ltd Backend Developer Assessment**.

The system is designed with **clean architecture**, handles **high concurrency**, assigns beauticians based on geographic proximity, and is fully integrated with **Supabase (PostgreSQL)** and **Redis**.

---

## 🎯 Core Features Implemented

1. **Authentication (JWT)**: Secure role-based access control (`ADMIN`, `CUSTOMER`, `BEAUTICIAN`).
2. **Beautician Module**: Profile management, service listings, GPS coordinate setup, and availability toggles.
3. **Nearest-Neighbor Booking**: Implemented the Haversine formula to assign the *closest available beautician* to a customer automatically.
4. **Lifecycle Management**: End-to-end booking states: `REQUESTED` → `ACCEPTED` → `IN_PROGRESS` → `COMPLETED` / `CANCELLED`.
5. **Admin Dashboards**: APIs available for viewing and filtering all bookings globally.

## 🏗 Data Architecture
To adhere strictly to Clean Architecture principles and avoid unnecessary bloat for an MVP, the database is normalized into **3 Core Tables**:
1. **`users`**: Centralizes authentication credentials and role-based logic (`ADMIN`, `CUSTOMER`, `BEAUTICIAN`).
2. **`beautician_profiles`**: A 1-to-1 mapping for beauticians. Separates location, bio, and availability data from standard users to ensure data integrity and leaner queries.
3. **`bookings`**: The transaction layer tracking the relationship between customers and beauticians, maintaining the entire lifecycle and geographic service data.

## 🚀 Advanced Concurrency Handling (Bonus)
To guarantee zero double-bookings under heavy traffic, this project utilizes a **Two-Tier Locking Mechanism**:
1. **Redis Distributed Lock**: Uses a `SETNX` lock to synchronize workers across multiple instances.
2. **Atomic Updates**: Final assignment relies on an atomic SQL query (`UPDATE ... WHERE is_available = TRUE`) to completely eliminate race conditions.

## 🛠 Tech Stack
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL (via Supabase) with `asyncpg` driver
- **ORM**: SQLAlchemy 2.0 (AsyncSession)
- **Caching & Locking**: Redis
- **Authentication**: JWT (python-jose), bcrypt
- **Deployment**: Gunicorn + Uvicorn workers

---

## ⚙️ Local Setup Instructions

This project is configured to run effortlessly out-of-the-box by connecting directly to Supabase.

### 1. Requirements
- Python 3.10+
- A [Supabase](https://supabase.com/) project (Free Tier is fine)
- (Optional) Local Redis instance

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
# Essential
PROJECT_NAME="Atoma Beautician Booking API"
SECRET_KEY="your_super_secret_key"

# Database (From Supabase -> Settings -> Database -> Connection String -> URI)
# *IMPORTANT*: Use the Transaction Pooler URL (Port 6543)
DATABASE_URL="postgresql://postgres.xxxx:your_password@aws-0-xxxx.pooler.supabase.com:6543/postgres"

# Optional: Enables Distributed Locking
REDIS_URL="redis://localhost:6379/0"
```

### 3. Installation & Run
```bash
# Create virtual environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate.bat
# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations to build the tables on Supabase
python migrate.py

# Start the server
uvicorn app.main:app --reload
```
You can access the automated Swagger documentation at: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## ☁️ Deployment (Render.com)

The project includes a `render.yaml` file that allows for **one-click deployment** on Render.

1. Push this repository to GitHub.
2. Log into Render.com and go to **Blueprints** -> **New Blueprint Instance**.
3. Connect your GitHub repository.
4. Render will automatically read `render.yaml` and provision:
   - A Web Service for the backend running on `gunicorn`.
   - A free Redis instance (for internal locking).
5. Add your Supabase `DATABASE_URL` in the Render environment variables tab.
6. Click Deploy! 🚀

---

## 🧪 Testing

A comprehensive integration test simulates real-world load, including multi-role authentication flows and a 5-user concurrent double-booking attack.

```bash
python test_integration.py
```
*Observe the logs: 1 booking will succeed, and 4 will be cleanly rejected.*
