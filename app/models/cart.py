from datetime import datetime
from app.models.db import db

class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate cart items
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),)
    
    @property
    def product_name(self):
        return self.product.name if self.product else 'Product'

    @property
    def price(self):
        return float(self.product.price) if self.product else 0.0

    @property
    def image(self):
        if self.product and self.product.images and len(self.product.images) > 0:
            return self.product.images[0]
        return None

    def get_total(self):
        if self.product:
            return self.quantity * float(self.product.price)
        return 0.0

    def __getitem__(self, item):
        return getattr(self, item)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'product_id': str(self.product_id),
            'product_name': self.product_name,
            'price': self.price,
            'quantity': self.quantity,
            'image': self.image,
            'total': self.get_total(),
            'product': self.product.to_dict() if self.product else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
