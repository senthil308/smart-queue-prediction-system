import requests

# Try login or register
resp = requests.post('http://127.0.0.1:5000/api/auth/register', json={"username": "testadmin99", "password": "123", "role": "admin"})
test_id = "testadmin99"
if resp.status_code == 201:
    test_id = resp.json().get('user_id')

resp = requests.post('http://127.0.0.1:5000/api/auth/login', json={"user_id": test_id, "password": "123"})
if resp.status_code == 200:
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post('http://127.0.0.1:5000/api/admin/queues', json={"name": "testqueue", "average_service_time": 5, "capacity": 20}, headers=headers)
    print("CREATE QUEUE STATUS:", r.status_code)
    print("CREATE QUEUE RESPONSE:", r.text)
    
    if r.status_code == 201:
        qid = r.json()['id']
        rd = requests.delete(f'http://127.0.0.1:5000/api/admin/queues/{qid}', headers=headers)
        print("DELETE QUEUE STATUS:", rd.status_code)
        print("DELETE QUEUE RESPONSE:", rd.text)
else:
    print("LOGIN FAILED:", resp.status_code, resp.text)
