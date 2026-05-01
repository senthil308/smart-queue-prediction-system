from extensions import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token_number = db.Column(db.Integer, nullable=False)
    queue_id = db.Column(db.Integer, db.ForeignKey('queues.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    status = db.Column(db.String(20), default='waiting') # waiting, serving, completed, cancelled
    estimated_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    served_at = db.Column(db.DateTime, nullable=True)
    actual_service_time = db.Column(db.Float, nullable=True)  # real time in minutes, recorded on completion

    # Relationships for transfers
    transfers = db.relationship('Transfer', backref='token_ref', lazy=True, primaryjoin="Token.id == Transfer.token_id")

    def to_dict(self):
        return {
            'id': self.id,
            'token_number': self.token_number,
            'queue_id': self.queue_id,
            'user_id': self.user_id,
            'admin_id': self.admin_id,
            'status': self.status,
            'estimated_time': self.estimated_time.isoformat() if self.estimated_time else None,
            'created_at': self.created_at.isoformat(),
            'served_at': self.served_at.isoformat() if self.served_at else None
        }
