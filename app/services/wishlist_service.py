from app.models.db import db
from app.models.wishlist import Wishlist
from app.models.product import Product
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class WishlistService:
    
    @staticmethod
    def add_to_wishlist(user_id: str, product_id: str) -> Dict:
        """
        Add product to wishlist
        """
        try:
            # Check if already in wishlist
            existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
            if existing:
                return {
                    'success': False,
                    'message': 'Product already in wishlist'
                }
            
            wishlist_item = Wishlist(
                id=str(uuid.uuid4()),
                user_id=user_id,
                product_id=product_id
            )
            
            db.session.add(wishlist_item)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Product added to wishlist'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add to wishlist error: {str(e)}")
            return {
                'success': False,
                'message': f'Add to wishlist failed: {str(e)}'
            }
    
    @staticmethod
    def remove_from_wishlist(user_id: str, product_id: str) -> Dict:
        """
        Remove product from wishlist
        """
        try:
            wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
            if wishlist_item:
                db.session.delete(wishlist_item)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Product removed from wishlist'
                }
            return {
                'success': False,
                'message': 'Product not in wishlist'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Remove from wishlist error: {str(e)}")
            return {
                'success': False,
                'message': f'Remove from wishlist failed: {str(e)}'
            }
    
    @staticmethod
    def get_user_wishlist(user_id: str) -> List[Wishlist]:
        """
        Get user's wishlist with product details
        """
        try:
            return Wishlist.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logger.error(f"Get user wishlist error: {str(e)}")
            return []
    
    @staticmethod
    def is_in_wishlist(user_id: str, product_id: str) -> bool:
        """
        Check if product is in user's wishlist
        """
        try:
            return Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first() is not None
        except Exception as e:
            logger.error(f"Check wishlist error: {str(e)}")
            return False
    
    @staticmethod
    def clear_wishlist(user_id: str) -> Dict:
        """
        Clear user's wishlist
        """
        try:
            Wishlist.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return {
                'success': True,
                'message': 'Wishlist cleared'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clear wishlist error: {str(e)}")
            return {
                'success': False,
                'message': f'Clear wishlist failed: {str(e)}'
            }
