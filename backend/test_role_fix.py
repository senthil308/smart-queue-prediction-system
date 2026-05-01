import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_admin_booking():
    # 1. Register Admin (optional, might already exist)
    print("Registering Admin...")
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "username": "senthiladmin",
        "password": "password",
        "role": "admin"
    })
    print(f"Register Status: {reg_res.status_code}")
    if reg_res.status_code != 201:
        try:
            err_msg = reg_res.json().get('error')
        except:
            err_msg = reg_res.text
        print(f"Registration skipped or failed: {err_msg}")

    # 2. Login as Admin
    print("\nLogging in as Admin...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "senthiladmin",
        "password": "password",
        "role": "admin"
    })
    if login_res.status_code != 200:
        print(f"Login Failed with status {login_res.status_code}")
        print(f"Login Response Content: {login_res.text}")
        return
        
    try:
        login_data = login_res.json()
    except Exception as e:
        print(f"Failed to parse login response as JSON: {e}")
        print(f"Raw Response: {login_res.text}")
        return

    token = login_data.get("token")
    print(f"Login Status: {login_res.status_code}, Token obtained: {token is not None}")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create a Queue
    print("\nCreating a Queue...")
    # The correct endpoint is /admin/queues (POST)
    queue_res = requests.post(f"{BASE_URL}/admin/queues", json={
        "name": "Test Queue " + str(datetime.now().timestamp()), # Unique name
        "average_service_time": 5,
        "capacity": 10
    }, headers=headers)
    print(f"Create Queue Status: {queue_res.status_code}")
    if queue_res.status_code not in [201, 200]:
        print(f"Create Queue Failed: {queue_res.json()}")
        return
        
    queue_data = queue_res.json()
    queue_id = queue_data.get("id")
    print(f"Queue ID: {queue_id}")

    # 4. Book a Token
    print(f"\nBooking a Token for Queue ID {queue_id}...")
    book_res = requests.post(f"{BASE_URL}/tokens/book", json={
        "queue_id": queue_id
    }, headers=headers)
    print(f"Book Token Status: {book_res.status_code}, Response: {book_res.json()}")

    # 5. Verify My Tokens
    print("\nGetting My Tokens...")
    tokens_res = requests.get(f"{BASE_URL}/tokens/my_tokens", headers=headers)
    print(f"Get Tokens Status: {tokens_res.status_code}, Response: {tokens_res.json()}")

if __name__ == "__main__":
    from datetime import datetime
    test_admin_booking()
