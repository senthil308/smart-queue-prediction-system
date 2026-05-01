import os
import sys
sys.path.append(os.getcwd())

from app import create_app
from extensions import db
from models.user import User
from models.admin import Admin

def check_db():
    app = create_app()
    with app.app_context():
        print("--- Users ---")
        users = User.query.all()
        for u in users:
            print(f"ID: {u.id}, Username: {u.username}")
            
        print("\n--- Admins ---")
        admins = Admin.query.all()
        for a in admins:
            print(f"ID: {a.id}, Username: {a.username}")

if __name__ == "__main__":
    check_db()
