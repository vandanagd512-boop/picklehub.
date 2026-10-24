from datetime import datetime
from typing import Optional
from enum import Enum
from app.models.db import db

class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.String(36), primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    coupon_type = db.Column(db.Enum(CouponType), default=CouponType.PERCENTAGE, nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    min_order_value = db.Column(db.Numeric(10, 2), default=0)
    max_discount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0, nullable=False)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def is_valid(self):
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, order_total: float):
        if not self.is_valid() or order_total < float(self.min_order_value):
            return 0.0
        
        c_type = self.coupon_type.value if isinstance(self.coupon_type, CouponType) else str(self.coupon_type)
        if c_type == 'percentage':
            discount = order_total * (float(self.value) / 100)
            if self.max_discount:
                discount = min(discount, float(self.max_discount))
        else:
            discount = float(self.value)
        
        return round(discount, 2)
    
    def __getitem__(self, item):
        return getattr(self, item)

    def to_dict(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'coupon_type': self.coupon_type.value if isinstance(self.coupon_type, CouponType) else str(self.coupon_type),
            'value': float(self.value),
            'min_order_value': float(self.min_order_value),
            'max_discount': float(self.max_discount) if self.max_discount else None,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
