from app.models.db import db
from app.models.user import User, UserRole
from flask_login import login_user, logout_user
from typing import Optional, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def register(email: str, password: str, full_name: str, role: str = 'customer', phone: str = None) -> Dict:
        """
        Register a new user using local database
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                full_name=full_name,
                phone=phone,
                role=UserRole(role) if isinstance(role, str) else role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user
            }
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
    
    @staticmethod
    def login(email: str, password: str) -> Dict:
        """
        Login user using local database
        """
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    return {
                        'success': False,
                        'message': 'Account is deactivated'
                    }
                
                login_user(user)
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }
    
    @staticmethod
    def logout() -> Dict:
        """
        Logout user
        """
        try:
            logout_user()
            return {
                'success': True,
                'message': 'Logout successful'
            }
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                'success': False,
                'message': f'Logout failed: {str(e)}'
            }
    
    @staticmethod
    def verify_email(user_id: str) -> Dict:
        """
        Verify user email
        """
        try:
            user = User.query.get(user_id)
            if user:
                user.is_verified = True
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Email verified successfully'
                }
            return {
                'success': False,
                'message': 'User not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Email verification error: {str(e)}")
            return {
                'success': False,
                'message': f'Email verification failed: {str(e)}'
            }
    
    @staticmethod
    def reset_password(email: str) -> Dict:
        """
        Send password reset email (placeholder - needs email service integration)
        """
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                # TODO: Implement email sending with reset token
                return {
                    'success': True,
                    'message': 'Password reset email sent'
                }
            return {
                'success': False,
                'message': 'Email not found'
            }
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {
                'success': False,
                'message': f'Password reset failed: {str(e)}'
            }
    
    @staticmethod
    def update_password(user_id: str, new_password: str) -> Dict:
        """
        Update user password
        """
        try:
            user = User.query.get(user_id)
            if user:
                user.set_password(new_password)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Password updated successfully'
                }
            return {
                'success': False,
                'message': 'User not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password update error: {str(e)}")
            return {
                'success': False,
                'message': f'Password update failed: {str(e)}'
            }
    
    @staticmethod
    def get_current_user(user_id: str) -> Optional[User]:
        """
        Get current user from session
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Get current user error: {str(e)}")
        return None
