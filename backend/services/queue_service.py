from extensions import db, socketio
from models.queue import Queue
from models.token import Token
from datetime import datetime

def get_queue_status(queue_id):
    queue = Queue.query.get(queue_id)
    if not queue:
        return None
    
    waiting_count = Token.query.filter_by(queue_id=queue_id, status='waiting').count()
    serving_token = Token.query.filter_by(queue_id=queue_id, status='serving').first()

    from services.prediction_service import predict_service_time
    predicted_avg = predict_service_time(queue)

    from datetime import datetime
    if serving_token and serving_token.served_at:
        elapsed_min = (datetime.utcnow() - serving_token.served_at).total_seconds() / 60.0
        rem_serving = max(0, predicted_avg - elapsed_min)
        estimated_wait_time = int(round(rem_serving + (waiting_count * predicted_avg)))
    else:
        estimated_wait_time = int(round(waiting_count * predicted_avg))

    return {
        'queue_id': queue.id,
        'queue_name': queue.name,
        'is_active': queue.is_active,
        'waiting_count': waiting_count,
        'capacity': queue.capacity,
        'total_issued': Token.query.filter_by(queue_id=queue_id).filter(Token.status != 'cancelled').count(),
        'serving_token': serving_token.token_number if serving_token else None,
        'estimated_wait_time': estimated_wait_time
    }

def broadcast_queue_update(queue_id):
    status = get_queue_status(queue_id)
    if status:
        # Emit to a specific room for this queue
        socketio.emit('queue_update', status, to=f'queue_{queue_id}')
        # Also emit globally for the dashboard
        socketio.emit('global_queue_update', status)
