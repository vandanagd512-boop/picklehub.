from app.models.db import db
from app.models.user import User, UserRole
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class UserService:
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        Get user by ID
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
        return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email
        """
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
        return None
    
    @staticmethod
    def update_user(user_id: str, data: Dict) -> Dict:
        """
        Update user profile
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update user error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def update_profile_image(user_id: str, image_url: str) -> Dict:
        """
        Update user profile image
        """
        return UserService.update_user(user_id, {'profile_image': image_url})
    
    @staticmethod
    def get_all_sellers() -> List[User]:
        """
        Get all sellers
        """
        try:
            return User.query.filter_by(role=UserRole.SELLER, is_active=True).all()
        except Exception as e:
            logger.error(f"Get sellers error: {str(e)}")
            return []
    
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all users with pagination (admin only)
        """
        try:
            pagination = User.query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'users': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get all users error: {str(e)}")
            return {'users': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def deactivate_user(user_id: str) -> Dict:
        """
        Deactivate user account (admin only)
        """
        return UserService.update_user(user_id, {'is_active': False})
    
    @staticmethod
    def activate_user(user_id: str) -> Dict:
        """
        Activate user account (admin only)
        """
        return UserService.update_user(user_id, {'is_active': True})
    
    @staticmethod
    def verify_user(user_id: str) -> Dict:
        """
        Verify user account (admin only)
        """
        return UserService.update_user(user_id, {'is_verified': True})
    
    @staticmethod
    def change_role(user_id: str, new_role: str) -> Dict:
        """
        Change user role (admin only)
        """
        if new_role not in ['customer', 'seller', 'admin']:
            return {
                'success': False,
                'message': 'Invalid role'
            }
        return UserService.update_user(user_id, {'role': UserRole(new_role)})
