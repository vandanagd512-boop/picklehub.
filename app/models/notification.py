from datetime import datetime
from typing import Optional
from enum import Enum
from app.models.db import db

class NotificationType(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    PRODUCT = "product"
    PROMOTION = "promotion"
    SYSTEM = "system"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    notification_type = db.Column(db.String(50), default='system', nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))
    
    def __getitem__(self, item):
        return getattr(self, item)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
