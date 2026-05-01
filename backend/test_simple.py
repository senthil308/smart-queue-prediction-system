import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"

def test():
    print("1. Registration...")
    r = requests.post(f"{BASE_URL}/auth/register", json={"username":"senthiladmin","password":"password","role":"admin"})
    print(f"Status: {r.status_code}")
    print(f"Text: {r.text[:200]}")

    print("\n2. Login...")
    r = requests.post(f"{BASE_URL}/auth/login", json={"username":"senthiladmin","password":"password","role":"admin"})
    print(f"Status: {r.status_code}")
    print(f"Text: {r.text[:200]}")
    
    try:
        token = r.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n3. Create Queue...")
        r = requests.post(f"{BASE_URL}/admin/queues", json={"name":f"Q_{int(datetime.now().timestamp())}"}, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Text: {r.text[:200]}")
        qid = r.json().get('id')
        
        print(f"\n4. Book Token (QID {qid})...")
        r = requests.post(f"{BASE_URL}/tokens/book", json={"queue_id":qid}, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Text: {r.text[:200]}")
        
    except Exception as e:
        print(f"Error in chain: {e}")

if __name__ == "__main__":
    test()
