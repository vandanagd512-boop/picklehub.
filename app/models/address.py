from datetime import datetime
from typing import Optional
from enum import Enum
from app.models.db import db

class AddressType(str, Enum):
    HOME = "home"
    WORK = "work"
    OTHER = "other"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class Address(db.Model):
    __tablename__ = 'addresses'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    address_type = db.Column(db.Enum(AddressType), default=AddressType.HOME, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    address_line2 = db.Column(db.String(255))
    country = db.Column(db.String(100), default='India')
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def get_full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.city, self.state, self.postal_code, self.country])
        return ', '.join([p for p in parts if p])
    
    def __getitem__(self, item):
        return getattr(self, item)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'address_type': self.address_type.value if isinstance(self.address_type, AddressType) else str(self.address_type),
            'full_name': self.full_name,
            'phone': self.phone,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
