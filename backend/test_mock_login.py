import os
import sys
import json
from flask import request

sys.path.append(os.getcwd())

from app import create_app
from auth.routes import auth_bp
from extensions import db

def test_mock_login():
    app = create_app()
    # We need to use the app's test client or a request context
    with app.test_request_context(
        '/api/auth/login',
        method='POST',
        data=json.dumps({"username": "senthiladmin", "password": "password", "role": "admin"}),
        content_type='application/json'
    ):
        from auth.routes import login
        try:
            response, status = login()
            print(f"Response: {response.get_json()}, Status: {status}")
        except Exception as e:
            import traceback
            print(f"CRASH: {e}")
            print(traceback.format_exc())

if __name__ == "__main__":
    test_mock_login()
