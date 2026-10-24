from app.models.db import db
from app.models.coupon import Coupon, CouponType
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class CouponService:
    
    @staticmethod
    def create_coupon(data: Dict) -> Dict:
        """
        Create a new coupon
        """
        try:
            coupon = Coupon(
                id=str(uuid.uuid4()),
                code=data['code'].upper(),
                coupon_type=CouponType(data.get('coupon_type', 'percentage')),
                value=data['value'],
                min_order_value=data.get('min_order_value', 0),
                max_discount=data.get('max_discount'),
                usage_limit=data.get('usage_limit'),
                valid_from=data.get('valid_from'),
                valid_until=data.get('valid_until'),
                is_active=data.get('is_active', True),
                description=data.get('description')
            )
            
            db.session.add(coupon)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Coupon created successfully',
                'coupon': coupon
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create coupon error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_coupon_by_id(coupon_id: str) -> Optional[Coupon]:
        """
        Get coupon by ID
        """
        try:
            return Coupon.query.get(coupon_id)
        except Exception as e:
            logger.error(f"Get coupon error: {str(e)}")
        return None
    
    @staticmethod
    def get_coupon_by_code(code: str) -> Optional[Coupon]:
        """
        Get coupon by code
        """
        try:
            return Coupon.query.filter_by(code=code.upper()).first()
        except Exception as e:
            logger.error(f"Get coupon by code error: {str(e)}")
        return None
    
    @staticmethod
    def get_all_coupons(active_only: bool = True, page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all coupons
        """
        try:
            query = Coupon.query
            if active_only:
                query = query.filter_by(is_active=True)
            
            pagination = query.order_by(Coupon.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'coupons': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get all coupons error: {str(e)}")
            return {'coupons': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def validate_coupon(code: str, order_total: float) -> Dict:
        """
        Validate coupon and calculate discount
        """
        try:
            coupon = CouponService.get_coupon_by_code(code)
            
            if not coupon:
                return {
                    'valid': False,
                    'message': 'Invalid coupon code'
                }
            
            if not coupon.is_valid():
                return {
                    'valid': False,
                    'message': 'Coupon is expired or inactive'
                }
            
            if order_total < float(coupon.min_order_value):
                return {
                    'valid': False,
                    'message': f'Minimum order value of ₹{coupon.min_order_value} required'
                }
            
            discount = coupon.calculate_discount(order_total)
            
            return {
                'valid': True,
                'coupon': coupon,
                'discount': discount,
                'message': f'Coupon applied! You save ₹{discount}'
            }
        except Exception as e:
            logger.error(f"Validate coupon error: {str(e)}")
            return {
                'valid': False,
                'message': f'Validation failed: {str(e)}'
            }
    
    @staticmethod
    def use_coupon(coupon_id: str) -> Dict:
        """
        Increment coupon usage count
        """
        try:
            coupon = Coupon.query.get(coupon_id)
            if coupon:
                coupon.used_count += 1
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Coupon usage recorded'
                }
            return {
                'success': False,
                'message': 'Coupon not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Use coupon error: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to record usage: {str(e)}'
            }
    
    @staticmethod
    def update_coupon(coupon_id: str, data: Dict) -> Dict:
        """
        Update coupon
        """
        try:
            coupon = Coupon.query.get(coupon_id)
            if not coupon:
                return {
                    'success': False,
                    'message': 'Coupon not found'
                }
            
            for key, value in data.items():
                if hasattr(coupon, key):
                    setattr(coupon, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Coupon updated successfully',
                'coupon': coupon
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update coupon error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def delete_coupon(coupon_id: str) -> Dict:
        """
        Delete coupon
        """
        try:
            coupon = Coupon.query.get(coupon_id)
            if coupon:
                db.session.delete(coupon)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Coupon deleted successfully'
                }
            return {
                'success': False,
                'message': 'Coupon not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete coupon error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
