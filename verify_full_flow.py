import requests
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def log(msg):
    with open("verification.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_backend():
    with open("verification.log", "w", encoding="utf-8") as f:
        f.write("Starting Verification...\n")

    log(f"Testing connectivity to {BASE_URL}...")
    
    import uuid
    # 1. Register a test user
    email = f"verification_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    
    log(f"\n[1] Attempting to Register user: {email}")
    try:
        register_payload = {
            "name": "Verification User",
            "email": email,
            "password": password
        }
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
        
        if reg_response.status_code == 201:
            log("✅ Registration Successful")
        elif reg_response.status_code == 400 and "User already exists" in reg_response.text:
            log("ℹ️ User already exists, proceeding to login...")
        else:
            log(f"❌ Registration Failed: {reg_response.status_code} - {reg_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        log("❌ CRITICAL: Could not connect to backend. Is it running on port 5000?")
        return False

    # 2. Login
    log(f"\n[2] Attempting to Login...")
    login_payload = {
        "email": email,
        "password": password
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if login_response.status_code != 200:
        log(f"❌ Login Failed: {login_response.status_code} - {login_response.text}")
        return False
    
    data = login_response.json()
    access_token = data.get('access_token')
    user_data = data.get('user')
    
    if not access_token:
        log("❌ Login succeeded but no access_token returned!")
        return False
        
    log(f"✅ Login Successful. Token received.")
    name_check = user_data.get('name', 'N/A')
    log(f"   User Name: {name_check}")
    if name_check != "Verification User":
        log(f"❌ Name mismatch! Expected 'Verification User', got '{name_check}'")
        return False
        
    log(f"   User Role: {user_data.get('role', {}).get('name') if user_data.get('role') else 'N/A'}")

    # 3. Fetch Protected Resource (Employees)
    log(f"\n[3] Attempting to fetch Protected Resource (/employees)...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    employees_response = requests.get(f"{BASE_URL}/employees", headers=headers)
    
    if employees_response.status_code == 200:
        log(f"✅ Protected Resource Access Successful")
        log(f"   Employees found: {len(employees_response.json())}")
        return True
    else:
        log(f"❌ Protected Resource Access Failed: {employees_response.status_code} - {employees_response.text}")
        return False

if __name__ == "__main__":
    success = test_backend()
    if success:
        log("\n🎉 BACKEND CONNECTION VERIFIED! The API is working correctly.")
        sys.exit(0)
    else:
        log("\n⚠️ BACKEND CONNECTION FAILED.")
        sys.exit(1)
