import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def get_token(email, password):
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            return resp.json()['access_token']
        print(f"Login failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Login error: {e}")
    return None

def test_leave_request(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "leave_type": "Sick Leave",
        "start_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "reason": "Testing leave request"
    }
    resp = requests.post(f"{BASE_URL}/leave", json=data, headers=headers)
    print(f"Leave Request POST: {resp.status_code}")
    if resp.status_code != 201:
        print(resp.json())
    return resp.status_code == 201

def test_payroll_run(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create a cycle
    cycle_data = {
        "name": "January 2024",
        "startDate": "2024-01-01",
        "endDate": "2024-01-31"
    }
    resp = requests.post(f"{BASE_URL}/payroll/cycles", json=cycle_data, headers=headers)
    print(f"Create Cycle POST: {resp.status_code}")
    
    cycle_id = None
    if resp.status_code == 400 and 'unique constraint' in resp.text.lower():
         # Maybe it exists?
         pass
    
    if resp.status_code != 201:
        # Try to get existing cycles
        resp = requests.get(f"{BASE_URL}/payroll/cycles", headers=headers)
        cycles = resp.json()
        active_cycle = next((c for c in cycles if c['status'] == 'Active'), None)
        if active_cycle:
            cycle_id = active_cycle['id']
            print(f"Using existing active cycle: {cycle_id}")
    else:
        cycle_id = resp.json()['id']
        print(f"Created new cycle: {cycle_id}")
        
    if not cycle_id:
        print("No active cycle found or created.")
        return False
        
    # 2. Run payroll
    resp = requests.post(f"{BASE_URL}/payroll", json={"cycle_id": cycle_id}, headers=headers)
    print(f"Run Payroll POST: {resp.status_code}")
    if resp.status_code != 201:
        print(resp.json())
    return resp.status_code == 201

if __name__ == "__main__":
    # Get all users to find an admin
    token = get_token("admin@example.com", "admin123")
    if token:
        print("Logged in as admin")
        test_leave_request(token)
        test_payroll_run(token)
    else:
        # Try to find any user if admin fails
        print("Login failed, checking db for users...")
