import os
import sys
sys.path.append(os.getcwd())

# IMPORTANT: create the app FIRST so extensions are initialized before use
from app import create_app

app = create_app()

with app.app_context():
    from extensions import db, bcrypt
    from models.admin import Admin
    from models.user import User
    from models.queue import Queue

    db.create_all()

    # Reset (or create) senthiladmin with a fresh password hash
    admin = Admin.query.filter_by(username='senthiladmin').first()
    hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
    
    if admin:
        admin.password_hash = hashed_pw
        print("Updated senthiladmin password hash.")
    else:
        admin = Admin(username='senthiladmin', password_hash=hashed_pw)
        db.session.add(admin)
        print("Created senthiladmin.")
    
    db.session.commit()

    # Also create a regular user for testing
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user_hash = bcrypt.generate_password_hash('password').decode('utf-8')
        user = User(username='testuser', password_hash=user_hash)
        db.session.add(user)
        db.session.commit()
        print("Created testuser.")
    else:
        print("testuser already exists.")

    # Create a test queue if needed
    queue = Queue.query.first()
    if not queue:
        queue = Queue(name="Test Queue", average_service_time=5, capacity=10)
        db.session.add(queue)
        db.session.commit()
        print("Created Test Queue.")
    else:
        print(f"Queue already exists: {queue.name} (id={queue.id})")
    
    print("Done.")
