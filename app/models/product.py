from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.models.db import db

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    PENDING = "pending"

    def __str__(self):
        return self.value

    def __html__(self):
        return self.value

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    discount_percentage = db.Column(db.Numeric(5, 2))
    stock = db.Column(db.Integer, default=0, nullable=False)
    images = db.Column(db.JSON, default=list)
    status = db.Column(db.Enum(ProductStatus), default=ProductStatus.ACTIVE, nullable=False)
    ingredients = db.Column(db.Text)
    spice_level = db.Column(db.String(50))
    shelf_life = db.Column(db.String(100))
    weight = db.Column(db.String(50))
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)
    review_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    seller = db.relationship('User', backref='products')
    category = db.relationship('Category', backref='products')
    cart_items = db.relationship('Cart', backref='product', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)
    
    def is_in_stock(self):
        st = self.status.value if isinstance(self.status, ProductStatus) else str(self.status)
        return self.stock > 0 and st.lower() == 'active'
    
    def get_discounted_price(self):
        if self.discount_percentage and self.original_price:
            return float(self.original_price) * (1 - float(self.discount_percentage) / 100)
        return float(self.price)
    
    def __getitem__(self, item):
        return getattr(self, item)

    def to_dict(self):
        return {
            'id': str(self.id),
            'seller_id': str(self.seller_id),
            'category_id': str(self.category_id),
            'category_name': self.category.name if self.category else None,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'original_price': float(self.original_price) if self.original_price else None,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else None,
            'stock': self.stock,
            'images': self.images or [],
            'status': self.status.value if isinstance(self.status, ProductStatus) else str(self.status),
            'ingredients': self.ingredients,
            'spice_level': self.spice_level,
            'shelf_life': self.shelf_life,
            'weight': self.weight,
            'is_featured': self.is_featured,
            'rating': float(self.rating),
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
