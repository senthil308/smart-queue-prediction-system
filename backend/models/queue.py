from extensions import db
from datetime import datetime

class Queue(db.Model):
    __tablename__ = 'queues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    average_service_time = db.Column(db.Integer, default=5) # Minutes per token
    capacity = db.Column(db.Integer, default=20) # Max tokens allowed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tokens = db.relationship('Token', backref='queue', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'average_service_time': self.average_service_time,
            'capacity': self.capacity,
            'created_at': self.created_at.isoformat()
        }
