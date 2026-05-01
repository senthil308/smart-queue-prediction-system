from flask import Blueprint, request, jsonify
from extensions import db
from models.queue import Queue
from models.transfer import Transfer
from models.token import Token
from models.admin import Admin
from utils.decorators import admin_required
from services.queue_service import broadcast_queue_update

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/queues', methods=['GET'])
@admin_required()
def get_all_queues():
    queues = Queue.query.all()
    from services.queue_service import get_queue_status
    result = [get_queue_status(q.id) for q in queues]
    return jsonify(result), 200

@admin_bp.route('/queues/<int:queue_id>/tokens/<int:token_number>/reassign', methods=['POST'])
@admin_required()
def reassign_token(queue_id, token_number):
    """Recycle a cancelled token (from a transfer) and reassign it to a new user."""
    data = request.get_json()
    to_username = data.get('username')
    to_role = data.get('role', 'user')

    if not to_username:
        return jsonify({"error": "Username is required"}), 400

    # Find the cancelled token by number in this queue
    token = Token.query.filter_by(queue_id=queue_id, token_number=token_number, status='cancelled').first()
    if not token:
        return jsonify({"error": "No cancelled token with that number found in this queue"}), 404

    from models.user import User
    if to_role == 'admin':
        new_owner = Admin.query.filter_by(username=to_username).first()
        if not new_owner:
            return jsonify({"error": f"Admin '{to_username}' not found"}), 404
        token.user_id = None
        token.admin_id = new_owner.id
    else:
        new_owner = User.query.filter_by(username=to_username).first()
        if not new_owner:
            return jsonify({"error": f"User '{to_username}' not found"}), 404
        token.user_id = new_owner.id
        token.admin_id = None

    token.status = 'waiting'  # put back in queue
    db.session.commit()
    broadcast_queue_update(queue_id)
    return jsonify({"message": f"Token #{token_number} successfully reassigned to {to_username}!"}), 200


@admin_bp.route('/queues', methods=['POST'])
@admin_required()
def create_queue():
    data = request.get_json()
    name = data.get('name')
    avg_time = data.get('average_service_time', 5)
    capacity = data.get('capacity', 20)

    if not name:
        return jsonify({"error": "Queue name is required"}), 400

    queue = Queue(name=name, average_service_time=avg_time, capacity=capacity)
    db.session.add(queue)
    db.session.commit()

    return jsonify(queue.to_dict()), 201

@admin_bp.route('/transfers', methods=['GET'])
@admin_required()
def get_pending_transfers():
    transfers = Transfer.query.filter_by(status='pending').all()
    return jsonify([t.to_dict() for t in transfers]), 200

@admin_bp.route('/queues/<int:queue_id>/capacity', methods=['POST'])
@admin_required()
def update_capacity(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue:
        return jsonify({"error": "Queue not found"}), 404
    data = request.get_json()
    queue.capacity = data.get('capacity', queue.capacity)
    db.session.commit()
    broadcast_queue_update(queue_id)
    return jsonify({"message": "Capacity updated", "queue": queue.to_dict()}), 200

@admin_bp.route('/transfers/<int:transfer_id>/approve', methods=['POST'])
@admin_required()
def approve_transfer(transfer_id):
    transfer = Transfer.query.get(transfer_id)
    if not transfer:
        return jsonify({"error": "Transfer not found"}), 404
    if transfer.status != 'pending':
        return jsonify({"error": "Invalid transfer request status"}), 400
        
    token = Token.query.get(transfer.token_id)
    from models.user import User
    from models.admin import Admin
    
    to_user = User.query.filter_by(username=transfer.to_username).first()
    if to_user:
        token.user_id = to_user.id
        token.admin_id = None
    else:
        to_admin = Admin.query.filter_by(username=transfer.to_username).first()
        if to_admin:
            token.status = 'cancelled'  # admin accepting = removes from queue
            token.user_id = None
            token.admin_id = to_admin.id
        else:
            return jsonify({"error": "Target user not found"}), 404
            
    transfer.status = 'approved'
    db.session.commit()
    return jsonify({"message": "Transfer approved successfully"}), 200
    
    return jsonify({"error": "Token or target user not found, or token is no longer waiting"}), 400

@admin_bp.route('/transfers/<int:transfer_id>/reject', methods=['POST'])
@admin_required()
def reject_transfer(transfer_id):
    transfer = Transfer.query.get(transfer_id)
    if not transfer or transfer.status != 'pending':
        return jsonify({"error": "Invalid transfer request"}), 400

    transfer.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Transfer rejected"}), 200

@admin_bp.route('/queues/<int:queue_id>/next', methods=['POST'])
@admin_required()
def call_next_token(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue:
        return jsonify({"error": "Queue not found"}), 404

    current_msg = ""
    current = Token.query.filter_by(queue_id=queue_id, status='serving').first()
    if current:
        current.status = 'completed'
        current_msg = f"Token {current.token_number} is completed. "
        # Record actual real service time for ML training
        if current.served_at:
            from datetime import datetime
            actual_mins = (datetime.utcnow() - current.served_at).total_seconds() / 60.0
            current.actual_service_time = round(actual_mins, 2)

    from datetime import datetime
    next_token = Token.query.filter_by(queue_id=queue_id, status='waiting').order_by(Token.token_number).first()
    if next_token:
        next_token.status = 'serving'
        next_token.served_at = datetime.utcnow()
        message = f"{current_msg}Now calling Token {next_token.token_number}" if current_msg else f"Calling Token {next_token.token_number}"
        response_data = {"message": message, "token": next_token.to_dict()}
    else:
        message = f"{current_msg}No more tokens waiting." if current_msg else "No tokens waiting."
        response_data = {"message": message}

    db.session.commit()
    broadcast_queue_update(queue_id)
    return jsonify(response_data), 200

@admin_bp.route('/queues/<int:queue_id>/reset', methods=['POST'])
@admin_required()
def reset_queue(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue:
        return jsonify({"error": "Queue not found"}), 404
        
    from models.transfer import Transfer
    tokens = Token.query.filter_by(queue_id=queue_id).all()
    for t in tokens:
        transfers = Transfer.query.filter_by(token_id=t.id).all()
        for tr in transfers:
            db.session.delete(tr)
        db.session.delete(t)
        
    db.session.commit()
    broadcast_queue_update(queue_id)
    return jsonify({"message": "Queue reset: All tokens deleted"}), 200

@admin_bp.route('/queues/<int:queue_id>', methods=['DELETE'])
@admin_required()
def delete_queue(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue:
        return jsonify({"error": "Queue not found"}), 404
        
    from models.transfer import Transfer
    tokens = Token.query.filter_by(queue_id=queue_id).all()
    for t in tokens:
        transfers = Transfer.query.filter_by(token_id=t.id).all()
        for tr in transfers:
            db.session.delete(tr)
        db.session.delete(t)
        
    db.session.delete(queue)
    db.session.commit()
    return jsonify({"message": "Queue permanently deleted"}), 200

@admin_bp.route('/queues/<int:queue_id>/tokens', methods=['GET'])
@admin_required()
def get_queue_tokens(queue_id):
    tokens = Token.query.filter_by(queue_id=queue_id).order_by(Token.token_number).all()
    return jsonify([t.to_dict() for t in tokens]), 200

@admin_bp.route('/tokens/<int:token_id>/cancel', methods=['POST'])
@admin_required()
def cancel_token(token_id):
    token = Token.query.get(token_id)
    if not token:
        return jsonify({"error": "Token not found"}), 404
    token.status = 'cancelled'
    db.session.commit()
    broadcast_queue_update(token.queue_id)
    return jsonify({"message": "Token cancelled"}), 200

@admin_bp.route('/queues/<int:queue_id>/offline_token', methods=['POST'])
@admin_required()
def generate_offline_token(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue or not queue.is_active:
        return jsonify({"error": "Invalid queue"}), 400

    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    # user = User.query.filter_by(user_id=get_jwt_identity()).first() # This line is no longer needed for offline tokens

    # Bypassing the check for duplicates because offline patients don't have accounts!
    total_tokens = Token.query.filter_by(queue_id=queue_id).count()
    if total_tokens >= queue.capacity:
        return jsonify({"error": "Queue capacity hit!"}), 400

    last_token = Token.query.filter_by(queue_id=queue_id).order_by(Token.token_number.desc()).first()
    next_number = 1 if not last_token else last_token.token_number + 1

    new_token = Token(token_number=next_number, queue_id=queue_id, user_id=None, status='waiting')
    db.session.add(new_token)
    db.session.commit()
    
    broadcast_queue_update(queue_id)
    return jsonify({"message": "Offline token generated", "token": new_token.to_dict()}), 201
