from flask import Blueprint, request, jsonify
from extensions import db
from models.token import Token
from models.queue import Queue
from models.user import User
from models.admin import Admin
from services.queue_service import broadcast_queue_update
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

tokens_bp = Blueprint('tokens', __name__)

@tokens_bp.route('/book', methods=['POST'])
@jwt_required()
def book_token():
    username = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')
    
    if role == 'admin':
        user_obj = Admin.query.filter_by(username=username).first()
        user_id = None
        admin_id = user_obj.id if user_obj else None
    else:
        user_obj = User.query.filter_by(username=username).first()
        user_id = user_obj.id if user_obj else None
        admin_id = None
    
    if not user_obj:
        return jsonify({"error": "User record not found"}), 404
    
    data = request.get_json()
    queue_id = data.get('queue_id')

    queue = Queue.query.get(queue_id)
    if not queue or not queue.is_active:
        return jsonify({"error": "Invalid or inactive queue"}), 400

    total_tokens = Token.query.filter_by(queue_id=queue_id).count()
    if total_tokens >= queue.capacity:
        return jsonify({"error": f"Queue Full. All {queue.capacity} tokens have been issued."}), 400

    if role == 'admin':
        existing_token = Token.query.filter_by(admin_id=admin_id, queue_id=queue_id).filter(Token.status.in_(['waiting', 'serving'])).first()
    else:
        existing_token = Token.query.filter_by(user_id=user_id, queue_id=queue_id).filter(Token.status.in_(['waiting', 'serving'])).first()
        
    if existing_token:
        return jsonify({"error": "User already has an active token in this queue"}), 400

    # Reuse a cancelled token number if available (avoids wasting numbers)
    recycled = Token.query.filter_by(queue_id=queue_id, status='cancelled').order_by(Token.token_number).first()
    if recycled:
        recycled.user_id = user_id
        recycled.admin_id = admin_id
        recycled.status = 'waiting'
        recycled.served_at = None
        recycled.actual_service_time = None
        db.session.commit()
        broadcast_queue_update(queue_id)
        return jsonify({"message": "Token booked successfully", "token": recycled.to_dict()}), 201

    last_token = Token.query.filter_by(queue_id=queue_id).order_by(Token.token_number.desc()).first()
    next_number = (last_token.token_number + 1) if last_token else 1

    new_token = Token(token_number=next_number, queue_id=queue_id, user_id=user_id, admin_id=admin_id)
    db.session.add(new_token)
    db.session.commit()

    broadcast_queue_update(queue_id)

    return jsonify({"message": "Token booked successfully", "token": new_token.to_dict()}), 201

@tokens_bp.route('/my_tokens', methods=['GET'])
@jwt_required()
def get_my_tokens():
    username = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')

    if role == 'admin':
        user_obj = Admin.query.filter_by(username=username).first()
        tokens = Token.query.filter_by(admin_id=user_obj.id).order_by(Token.created_at.desc()).all() if user_obj else []
    else:
        user_obj = User.query.filter_by(username=username).first()
        tokens = Token.query.filter_by(user_id=user_obj.id).order_by(Token.created_at.desc()).all() if user_obj else []
    result = []
    for t in tokens:
        d = t.to_dict()
        queue = Queue.query.get(t.queue_id)
        if queue:
            d['queue_name'] = queue.name
            from models.transfer import Transfer
            has_transfer = Transfer.query.filter_by(token_id=t.id, status='pending').first()
            d['is_transferring'] = True if has_transfer else False
            
            if t.status == 'waiting':
                # Count tokens ahead in queue — independent per token, no chaining
                ahead = Token.query.filter_by(queue_id=t.queue_id, status='waiting').filter(Token.token_number < t.token_number).count()
                d['people_ahead'] = ahead
                d['queue_position'] = ahead + 1  # 1-based position (1 = first)
                from services.prediction_service import predict_service_time
                predicted_avg = predict_service_time(queue)
                d['my_wait_time'] = round(ahead * predicted_avg, 1)
            else:
                d['people_ahead'] = 0
                d['queue_position'] = 0
                d['my_wait_time'] = 0
        else:
            d['people_ahead'] = 0
            d['queue_position'] = 0
            d['my_wait_time'] = 0
        result.append(d)
    return jsonify(result), 200
