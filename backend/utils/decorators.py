from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required, get_jwt
from models.user import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            role = claims.get('role', '')
            if str(role).lower() != 'admin':
                return jsonify({"error": f"Admins only! (Detected role: '{role}')"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
