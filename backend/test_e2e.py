import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"

def full_test():
    print("="*50)
    print("FULL END-TO-END ADMIN TOKEN BOOKING TEST")
    print("="*50)

    # 1. Login
    print("\n[1] Login as senthiladmin...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "senthiladmin", "password": "password", "role": "admin"
    })
    print(f"  Status: {r.status_code}")
    print(f"  Raw body: {r.text[:200]}")
    try:
        data = r.json()
    except Exception as e:
        print(f"  FAIL: Can't parse login response as JSON: {e}")
        return
    token = data.get('token')
    if not token:
        print(f"  FAIL: {data}")
        return
    print(f"  SUCCESS: Got JWT token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Queue
    print("\n[2] Create a new Queue...")
    q_name = f"TestQ_{int(datetime.now().timestamp())}"
    r = requests.post(f"{BASE_URL}/admin/queues", json={
        "name": q_name, "average_service_time": 5, "capacity": 20
    }, headers=headers)
    print(f"  Status: {r.status_code}")
    queue_data = r.json()
    queue_id = queue_data.get('id')
    if not queue_id:
        print(f"  FAIL: {queue_data}")
        return
    print(f"  SUCCESS: Queue created, ID={queue_id}")

    # 3. Book Token
    print(f"\n[3] Book Token for Queue ID {queue_id}...")
    r = requests.post(f"{BASE_URL}/tokens/book", json={"queue_id": queue_id}, headers=headers)
    print(f"  Status: {r.status_code}")
    token_data = r.json()
    print(f"  Response: {token_data}")
    if r.status_code in [200, 201]:
        print(f"  SUCCESS: Token booked!")
    else:
        print(f"  FAIL")
        return

    # 4. Check My Tokens
    print(f"\n[4] Check My Tokens...")
    r = requests.get(f"{BASE_URL}/tokens/my_tokens", headers=headers)
    print(f"  Status: {r.status_code}")
    my_tokens = r.json()
    print(f"  Found {len(my_tokens)} token(s)")
    for t in my_tokens:
        print(f"    Token #{t.get('token_number')} in queue '{t.get('queue_name')}' - Status: {t.get('status')}")

    print("\n" + "="*50)
    print("ALL TESTS PASSED!" if r.status_code == 200 else "SOME TESTS FAILED")
    print("="*50)

if __name__ == "__main__":
    full_test()
