from extensions import db
from datetime import datetime

class Transfer(db.Model):
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'), nullable=False)
    from_username = db.Column(db.String(100), nullable=False)
    to_username = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'token_id': self.token_id,
            'from_username': self.from_username,
            'to_username': self.to_username,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
