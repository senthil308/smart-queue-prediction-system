import os
import sys
sys.path.append(os.getcwd())

from app import create_app
from extensions import db, bcrypt
from models.user import User
from models.admin import Admin

def test_login():
    app = create_app()
    with app.app_context():
        username = "senthiladmin"
        password = "password"
        role = "admin"
        
        print(f"Testing login for {username} as {role}...")
        
        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:
            user = User.query.filter_by(username=username).first()
            
        print(f"User found: {user}")
        if user:
            print(f"User ID: {user.id}")
            print(f"Password hash exists: {user.password_hash is not None}")
            try:
                match = bcrypt.check_password_hash(user.password_hash, password)
                print(f"Password match: {match}")
            except Exception as e:
                print(f"Bcrypt error: {e}")
        else:
            print("User not found.")

if __name__ == "__main__":
    test_login()
