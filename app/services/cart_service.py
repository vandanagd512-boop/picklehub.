from app.models.db import db
from app.models.cart import Cart
from app.models.product import Product
from typing import Optional, Dict, List
import logging
import uuid

logger = logging.getLogger(__name__)

class CartService:
    
    @staticmethod
    def get_cart(user_id: str):
        """
        Get user's cart object with items and total calculation
        """
        try:
            items = Cart.query.filter_by(user_id=user_id).all()
            class UserCart:
                def __init__(self, cart_items):
                    self.items = cart_items
                def get_total(self):
                    return round(sum(item.get_total() for item in self.items), 2)
                def __bool__(self):
                    return len(self.items) > 0
            return UserCart(items)
        except Exception as e:
            logger.error(f"Get cart error: {str(e)}")
            class EmptyCart:
                items = []
                def get_total(self):
                    return 0.0
                def __bool__(self):
                    return False
            return EmptyCart()

    @staticmethod
    def get_cart_items(user_id: str) -> List[Cart]:
        """
        Get user's cart items
        """
        try:
            return Cart.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logger.error(f"Get cart error: {str(e)}")
            return []
    
    @staticmethod
    def add_to_cart(user_id: str, product_id: str, quantity: int = 1) -> Dict:
        """
        Add item to cart
        """
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return {
                    'success': False,
                    'message': 'Product not found'
                }
            
            if not product.is_in_stock():
                return {
                    'success': False,
                    'message': 'Product is out of stock'
                }
            
            if quantity > product.stock:
                return {
                    'success': False,
                    'message': f'Only {product.stock} items available'
                }
            
            # Check if item already exists in cart
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            
            if cart_item:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
            else:
                cart_item = Cart(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Item added to cart',
                'cart_item': cart_item
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add to cart error: {str(e)}")
            return {
                'success': False,
                'message': f'Add to cart failed: {str(e)}'
            }
    
    @staticmethod
    def remove_from_cart(user_id: str, product_id: str) -> Dict:
        """
        Remove item from cart
        """
        try:
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Item removed from cart'
                }
            
            return {
                'success': False,
                'message': 'Item not found in cart'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Remove from cart error: {str(e)}")
            return {
                'success': False,
                'message': f'Remove from cart failed: {str(e)}'
            }
    
    @staticmethod
    def update_cart_item(user_id: str, product_id: str, quantity: int) -> Dict:
        """
        Update cart item quantity
        """
        try:
            product = Product.query.get(product_id)
            
            if not product:
                return {
                    'success': False,
                    'message': 'Product not found'
                }
            
            if quantity > product.stock:
                return {
                    'success': False,
                    'message': f'Only {product.stock} items available'
                }
            
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            
            if cart_item:
                if quantity <= 0:
                    db.session.delete(cart_item)
                else:
                    cart_item.quantity = quantity
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Cart updated'
                }
            
            return {
                'success': False,
                'message': 'Item not found in cart'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update cart item error: {str(e)}")
            return {
                'success': False,
                'message': f'Update cart item failed: {str(e)}'
            }
    
    @staticmethod
    def clear_cart(user_id: str) -> Dict:
        """
        Clear user's cart
        """
        try:
            Cart.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return {
                'success': True,
                'message': 'Cart cleared'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clear cart error: {str(e)}")
            return {
                'success': False,
                'message': f'Clear cart failed: {str(e)}'
            }
    
    @staticmethod
    def get_cart_count(user_id: str) -> int:
        """
        Get total number of items in cart
        """
        try:
            cart_items = Cart.query.filter_by(user_id=user_id).all()
            return sum(item.quantity for item in cart_items)
        except Exception as e:
            logger.error(f"Get cart count error: {str(e)}")
            return 0
    
    @staticmethod
    def get_cart_total(user_id: str) -> float:
        """
        Get total cart value
        """
        try:
            cart_items = Cart.query.filter_by(user_id=user_id).all()
            return sum(item.get_total() for item in cart_items)
        except Exception as e:
            logger.error(f"Get cart total error: {str(e)}")
            return 0.0
