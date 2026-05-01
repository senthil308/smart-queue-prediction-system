from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models.user import User
from models.admin import Admin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    if role == 'admin':
        if Admin.query.filter_by(username=username).first():
            return jsonify({"error": "Admin username already taken"}), 400
        new_user = Admin(username=username, password_hash=hashed_pw)
    else:
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400
        new_user = User(username=username, password_hash=hashed_pw)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account registered successfully", "username": username}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')

        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:
            user = User.query.filter_by(username=username).first()

        with open('login_debug.txt', 'a') as f:
            f.write(f"Login attempt: {username}, role={role}, found={user}\n")
            if user:
                f.write(f"User found. ID: {user.id}\n")

        if user and hasattr(user, 'password_hash') and bcrypt.check_password_hash(user.password_hash, password):
            access_token = create_access_token(
                identity=user.username,
                additional_claims={"role": role}
            )
            return jsonify({
                "token": access_token,
                "user": {
                    "username": user.username,
                    "role": role
                }
            }), 200
        
        return jsonify({"error": "Invalid credentials"}), 401
        
    except Exception as e:
        import traceback
        with open('login_debug.txt', 'a') as f:
            f.write(f"GLOBAL ERROR in login: {e}\n{traceback.format_exc()}\n")
        return jsonify({"error": f"Internal server error: {e}"}), 500
