from flask import Blueprint, request, jsonify
from extensions import db
from models.token import Token
from models.transfer import Transfer
from models.user import User
from models.admin import Admin
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

sharing_bp = Blueprint('sharing', __name__)

@sharing_bp.route('/transfer', methods=['POST'])
@jwt_required()
def request_transfer():
    from_username = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')
    
    if role == 'admin':
        from_user = Admin.query.filter_by(username=from_username).first()
        from_user_id = None
        from_admin_id = from_user.id if from_user else None
    else:
        from_user = User.query.filter_by(username=from_username).first()
        from_user_id = from_user.id if from_user else None
        from_admin_id = None
        
    if not from_user:
        return jsonify({"error": "User record not found"}), 404

    data = request.get_json()
    token_number = data.get('token_id')  # frontend sends token_number as token_id
    to_username = data.get('to_username')

    # Look up by token_number owned by the current user (not DB id)
    if role == 'admin':
        token = Token.query.filter_by(token_number=token_number, admin_id=from_admin_id, status='waiting').first()
    else:
        token = Token.query.filter_by(token_number=token_number, user_id=from_user_id, status='waiting').first()

    if not token:
        return jsonify({"error": "Token not found, not yours, or not waiting"}), 400

    requested_role = data.get('to_role')

    if requested_role == 'admin':
        to_user = Admin.query.filter_by(username=to_username).first()
        to_role = 'admin'
    elif requested_role == 'user':
        to_user = User.query.filter_by(username=to_username).first()
        to_role = 'user'
    else:
        return jsonify({"error": "Target role (User/Admin) is required"}), 400
        
    if not to_user:
        return jsonify({"error": f"Target {to_role} '{to_username}' not found"}), 404

    if to_role == 'user':
        existing = Token.query.filter_by(user_id=to_user.id, queue_id=token.queue_id).filter(Token.status.in_(['waiting', 'serving'])).first()
    else:
        existing = Token.query.filter_by(admin_id=to_user.id, queue_id=token.queue_id).filter(Token.status.in_(['waiting', 'serving'])).first()
        
    if existing:
        return jsonify({"error": "Target user already has a token in this queue"}), 400

    new_transfer = Transfer(token_id=token.id, from_username=from_username, to_username=to_username)
    db.session.add(new_transfer)
    db.session.commit()

    return jsonify({"message": "Transfer requested successfully"}), 201

@sharing_bp.route('/my_transfers', methods=['GET'])
@jwt_required()
def get_my_transfers():
    username = get_jwt_identity()
    transfers = Transfer.query.filter_by(to_username=username, status='pending').all()
    return jsonify([t.to_dict() for t in transfers]), 200

@sharing_bp.route('/transfer/<int:transfer_id>/accept', methods=['POST'])
@jwt_required()
def accept_transfer(transfer_id):
    username = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')
    
    if role == 'admin':
        user_obj = Admin.query.filter_by(username=username).first()
    else:
        user_obj = User.query.filter_by(username=username).first()
    transfer = Transfer.query.get(transfer_id)
    
    if not transfer or transfer.to_username != username or transfer.status != 'pending':
        return jsonify({"error": "Invalid transfer"}), 400

    token = Token.query.get(transfer.token_id)
    if not token or token.status != 'waiting':
        return jsonify({"error": "Token is no longer valid"}), 400

    if role == 'admin':
        token.status = 'cancelled'  # admin accepting = removing from queue
        token.user_id = None
        token.admin_id = user_obj.id
        print(f"[ACCEPT] Admin accepted. token.id={token.id} cancelled. admin_id={user_obj.id}")
    else:
        token.user_id = user_obj.id
        token.admin_id = None
        print(f"[ACCEPT] User accepted. token.id={token.id}, status={token.status}")
        
    transfer.status = 'approved'
    db.session.commit()
    print(f"[ACCEPT] After commit: token.status={token.status}")

    return jsonify({"message": "Transfer accepted"}), 200

@sharing_bp.route('/transfer/<int:transfer_id>/reject', methods=['POST'])
@jwt_required()
def reject_transfer(transfer_id):
    username = get_jwt_identity()
    transfer = Transfer.query.get(transfer_id)
    if not transfer or transfer.to_username != username or transfer.status != 'pending':
        return jsonify({"error": "Invalid transfer"}), 400

    transfer.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Transfer rejected"}), 200

from sqlalchemy import or_

@sharing_bp.route('/history', methods=['GET'])
@jwt_required()
def get_transfer_history():
    username = get_jwt_identity()
    transfers = Transfer.query.filter(
        or_(Transfer.from_username == username, Transfer.to_username == username)
    ).order_by(Transfer.created_at.desc()).all()
    
    return jsonify([t.to_dict() for t in transfers]), 200
