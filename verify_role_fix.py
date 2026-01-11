import requests
import uuid

BASE_URL = "http://127.0.0.1:5000/api"

def verify_role_assignment():
    # 1. Test HR Registration
    hr_email = f"test_hr_{uuid.uuid4().hex[:6]}@example.com"
    print(f"\n[1] Registering HR User: {hr_email}")
    payload_hr = {
        "email": hr_email,
        "password": "password123",
        "name": "HR Test User",
        "role": "hr"
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload_hr)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # Login to verify role
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": hr_email, "password": "password123"})
        data = resp.json()
        role = data['user']['role']['name']
        print(f"   Assigned Role: {role}")
        
        if role == 'HR Manager':
            print("   ✅ HR Role Correct")
        else:
            print(f"   ❌ HR Role Incorrect (Expected 'HR Manager', got '{role}')")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 2. Test Employee Registration (Default/Explicit)
    emp_email = f"test_emp_{uuid.uuid4().hex[:6]}@example.com"
    print(f"\n[2] Registering Employee User: {emp_email}")
    payload_emp = {
        "email": emp_email,
        "password": "password123",
        "name": "Emp Test User",
        "role": "employee"
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload_emp)
        # Login to verify
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": emp_email, "password": "password123"})
        data = resp.json()
        role = data['user']['role']['name']
        print(f"   Assigned Role: {role}")
        
        if role == 'Employee':
             print("   ✅ Employee Role Correct")
        else:
             print(f"   ❌ Employee Role Incorrect (Expected 'Employee', got '{role}')")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    verify_role_assignment()
