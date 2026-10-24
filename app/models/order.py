from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.models.db import db

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class PaymentMethod(str, Enum):
    RAZORPAY = "razorpay"
    COD = "cod"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationship to Product
    product = db.relationship('Product', foreign_keys=[product_id], back_populates='order_items', lazy='joined')
    
    @property
    def product_name(self):
        if self.product and self.product.name:
            return self.product.name
        try:
            from app.models.product import Product
            p = Product.query.get(self.product_id)
            if p and p.name:
                return p.name
        except Exception:
            pass
        return 'Artisanal Pickle'

    def get_total(self):
        return self.quantity * float(self.price)
    
    def __getitem__(self, item):
        return getattr(self, item)

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'product_id': str(self.product_id),
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price),
            'total': self.get_total(),
            'product': self.product.to_dict() if self.product else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    shipping_address_id = db.Column(db.String(36), db.ForeignKey('addresses.id'))
    billing_address_id = db.Column(db.String(36), db.ForeignKey('addresses.id'))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), default=PaymentMethod.COD, nullable=False)
    payment_id = db.Column(db.String(255))
    coupon_code = db.Column(db.String(100))
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id])
    billing_address = db.relationship('Address', foreign_keys=[billing_address_id])
    
    def can_cancel(self):
        st = self.status.value if isinstance(self.status, OrderStatus) else str(self.status)
        return st.lower() in ['pending', 'confirmed']
    
    def can_track(self):
        st = self.status.value if isinstance(self.status, OrderStatus) else str(self.status)
        return st.lower() in ['confirmed', 'processing', 'shipped']
    
    @property
    def primary_product_name(self):
        if self.items and len(self.items) > 0:
            return self.items[0].product_name
        return 'Artisanal Pickle'
        
    @property
    def product_names_summary(self):
        if not self.items:
            return 'Artisanal Pickle'
        names = [item.product_name for item in self.items]
        if len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return f"{names[0]} & {names[1]}"
        else:
            return f"{names[0]} + {len(names) - 1} more"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'items': [item.to_dict() for item in self.items],
            'total_amount': float(self.total_amount),
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'billing_address': self.billing_address.to_dict() if self.billing_address else None,
            'status': self.status.value if isinstance(self.status, OrderStatus) else str(self.status),
            'payment_status': self.payment_status.value if isinstance(self.payment_status, PaymentStatus) else str(self.payment_status),
            'payment_method': self.payment_method.value if isinstance(self.payment_method, PaymentMethod) else str(self.payment_method),
            'payment_id': self.payment_id,
            'coupon_code': self.coupon_code,
            'discount_amount': float(self.discount_amount),
            'shipping_cost': float(self.shipping_cost),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
