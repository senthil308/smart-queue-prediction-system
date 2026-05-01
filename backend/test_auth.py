import requests

resp = requests.post('http://127.0.0.1:5000/api/auth/register', json={"username": "testauth1", "password": "123", "role": "admin"})
test_id = "testauth1"
if resp.status_code == 201:
    test_id = resp.json().get('user_id')

resp = requests.post('http://127.0.0.1:5000/api/auth/login', json={"user_id": test_id, "password": "123"})
if resp.status_code == 200:
    token = resp.json().get('token')
    print("RECEIVED TOKEN:", token[:10] + "..." if token else "NONE")
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post('http://127.0.0.1:5000/api/admin/queues', json={"name": "testqueue2", "average_service_time": 5, "capacity": 20}, headers=headers)
    print("CREATE QUEUE STATUS:", r.status_code)
    print("CREATE QUEUE RESPONSE:", r.text)
else:
    print("LOGIN FAILED:", resp.status_code, resp.text)
