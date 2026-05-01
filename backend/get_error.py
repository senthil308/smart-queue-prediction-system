import requests
import re

BASE_URL = "http://127.0.0.1:5000/api"

# Try login and get raw HTML on failure
r = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "senthiladmin",
    "password": "password",
    "role": "admin"
})

print(f"STATUS: {r.status_code}")

if r.status_code != 200:
    # Extract traceback from Flask debug HTML
    html = r.text
    # Find the traceback section
    match = re.search(r'<pre[^>]*>(.*?)</pre>', html, re.DOTALL)
    if match:
        import html as html_module
        tb = html_module.unescape(match.group(1))
        print("TRACEBACK FROM SERVER:")
        print(tb[:3000])
    else:
        # Just print first 2000 chars
        print("RAW RESPONSE (first 2000 chars):")
        print(html[:2000])
else:
    print(f"Login SUCCESS: {r.json()}")
