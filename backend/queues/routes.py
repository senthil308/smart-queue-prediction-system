from flask import Blueprint, jsonify
from models.queue import Queue
from services.queue_service import get_queue_status

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/', methods=['GET'])
def get_all_queues():
    queues = Queue.query.filter_by(is_active=True).all()
    result = []
    for q in queues:
        status = get_queue_status(q.id)
        if status:
            result.append(status)
    return jsonify(result), 200

@queue_bp.route('/<int:queue_id>', methods=['GET'])
def get_queue(queue_id):
    status = get_queue_status(queue_id)
    if not status:
        return jsonify({"error": "Queue not found"}), 404
    return jsonify(status), 200
