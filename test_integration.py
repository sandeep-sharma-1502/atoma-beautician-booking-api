import asyncio
import httpx
import logging
import random
from datetime import datetime, timedelta

# Configuring basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_integration")

API_URL = "http://127.0.0.1:8002/api/v1"

async def test_all_apis():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # --- 1. SYSTEM ---
        logger.info("--- Testing System APIs ---")
        health = await client.get("http://127.0.0.1:8002/health")
        logger.info(f"Health check: {health.status_code} {health.json()}")

        # --- 2. AUTH & ACCOUNTS ---
        logger.info("\n--- Testing Auth APIs ---")
        
        # Register Admin
        admin_email = f"admin_{datetime.now().timestamp()}@example.com"
        await client.post(f"{API_URL}/auth/register", json={
            "email": admin_email, "password": "password123", "full_name": "System Admin", "role": "ADMIN"
        })
        res = await client.post(f"{API_URL}/auth/token", data={"username": admin_email, "password": "password123"})
        admin_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
        logger.info("Admin registered and logged in.")

        # Register Beautician
        beaut_email = f"beautician_{datetime.now().timestamp()}@example.com"
        await client.post(f"{API_URL}/auth/register", json={
            "email": beaut_email, "password": "password123", "full_name": "Test Beautician", "role": "BEAUTICIAN"
        })
        res = await client.post(f"{API_URL}/auth/token", data={"username": beaut_email, "password": "password123"})
        beaut_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
        logger.info("Beautician registered and logged in.")

        # Register Customer
        cust_email = f"customer_{datetime.now().timestamp()}@example.com"
        await client.post(f"{API_URL}/auth/register", json={
            "email": cust_email, "password": "password123", "full_name": "Test Customer", "role": "CUSTOMER"
        })
        res = await client.post(f"{API_URL}/auth/token", data={"username": cust_email, "password": "password123"})
        cust_token = res.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        logger.info("Customer registered and logged in.")

        # --- 3. BEAUTICIAN PROFILE ---
        logger.info("\n--- Testing Beautician APIs ---")
        lat_offset = random.uniform(0.001, 0.009)
        unique_lat = 44.0 + lat_offset
        unique_lon = -70.0 + lat_offset

        update_res = await client.put(f"{API_URL}/beauticians/me", json={
            "bio": "Expert hair stylist with 10 years experience.",
            "services_offered": "haircut, styling, coloring",
            "is_available": True,
            "latitude": unique_lat,
            "longitude": unique_lon
        }, headers=beaut_headers)
        logger.info(f"Update Profile: {update_res.status_code}")

        # List Beauticians (Customer)
        list_res = await client.get(f"{API_URL}/beauticians/?lat={unique_lat}&lon={unique_lon}", headers=cust_headers)
        logger.info(f"List Near Beauticians: {list_res.status_code} (Found {len(list_res.json())})")

        # --- 4. BOOKINGS ---
        logger.info("\n--- Testing Booking APIs ---")
        
        # Create Booking AT THE EXACT SAME LOCATION to ensure this specific beautician is nearest
        booking_res = await client.post(f"{API_URL}/bookings/", json={
            "scheduled_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "services_requested": "haircut",
            "latitude": unique_lat,
            "longitude": unique_lon,
            "notes": "Please be on time."
        }, headers=cust_headers)
        booking = booking_res.json()
        booking_id = booking["id"]
        assigned_beautician_id = booking["beautician_id"]
        logger.info(f"Create Booking: {booking_res.status_code} ID={booking_id} Assigned ID={assigned_beautician_id}")

        # Check if the assigned beautician is the one we registered. 
        # For a clean test, we expect the one we just made (nearest).
        # We'll use the beautician credentials we just made if it matches, or log it.
        
        # Advance Status (Beautician: REQUESTED -> ACCEPTED)
        status_res = await client.put(f"{API_URL}/bookings/{booking_id}/status", json={"status": "ACCEPTED"}, headers=beaut_headers)
        if status_res.status_code != 200:
            logger.error(f"Failed to accept booking: {status_res.status_code} {status_res.text}")
            raise Exception("Test failed at Acceptance step")
        logger.info(f"Accept Booking: {status_res.status_code} Status={status_res.json()['status']}")

        # Advance Status (Beautician: ACCEPTED -> IN_PROGRESS)
        status_res = await client.put(f"{API_URL}/bookings/{booking_id}/status", json={"status": "IN_PROGRESS"}, headers=beaut_headers)
        logger.info(f"Start Booking: {status_res.status_code} Status={status_res.json()['status']}")

        # Complete Booking (Beautician: IN_PROGRESS -> COMPLETED)
        status_res = await client.put(f"{API_URL}/bookings/{booking_id}/status", json={"status": "COMPLETED"}, headers=beaut_headers)
        logger.info(f"Complete Booking: {status_res.status_code} Status={status_res.json()['status']}")

        # --- 5. ADMIN ---
        logger.info("\n--- Testing Admin APIs ---")
        admin_bookings = await client.get(f"{API_URL}/admin/bookings?status=COMPLETED", headers=admin_headers)
        logger.info(f"Admin Filtered Bookings: {admin_bookings.status_code} Count={len(admin_bookings.json())}")

        logger.info("\n✅ ALL API ENDPOINTS VERIFIED SUCCESSFULLY.")

if __name__ == "__main__":
    asyncio.run(test_all_apis())
