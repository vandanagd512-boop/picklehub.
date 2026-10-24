from app.models.db import db
from app.models.notification import Notification, NotificationType
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class NotificationService:
    
    @staticmethod
    def create_notification(user_id: str, notification_type: str, title: str, message: str, link: str = None) -> Dict:
        """
        Create a new notification
        """
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Notification created successfully',
                'notification': notification
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create notification error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_notification_by_id(notification_id: str) -> Optional[Notification]:
        """
        Get notification by ID
        """
        try:
            return Notification.query.get(notification_id)
        except Exception as e:
            logger.error(f"Get notification error: {str(e)}")
        return None
    
    @staticmethod
    def get_user_notifications(user_id: str, unread_only: bool = False, page: int = 1, per_page: int = 20) -> Dict:
        """
        Get user's notifications
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(is_read=False)
            
            pagination = query.order_by(Notification.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'notifications': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get user notifications error: {str(e)}")
            return {'notifications': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def mark_as_read(notification_id: str) -> Dict:
        """
        Mark notification as read
        """
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                notification.is_read = True
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Notification marked as read'
                }
            return {
                'success': False,
                'message': 'Notification not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Mark as read error: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to mark as read: {str(e)}'
            }
    
    @staticmethod
    def mark_all_as_read(user_id: str) -> Dict:
        """
        Mark all user notifications as read
        """
        try:
            Notification.query.filter_by(user_id=user_id).update({'is_read': True})
            db.session.commit()
            return {
                'success': True,
                'message': 'All notifications marked as read'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Mark all as read error: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to mark all as read: {str(e)}'
            }
    
    @staticmethod
    def delete_notification(notification_id: str) -> Dict:
        """
        Delete notification
        """
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                db.session.delete(notification)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Notification deleted successfully'
                }
            return {
                'success': False,
                'message': 'Notification not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete notification error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
    
    @staticmethod
    def get_unread_count(user_id: str) -> int:
        """
        Get count of unread notifications
        """
        try:
            return Notification.query.filter_by(user_id=user_id, is_read=False).count()
        except Exception as e:
            logger.error(f"Get unread count error: {str(e)}")
            return 0
    
    @staticmethod
    def notify_order_status(order_id: str, user_id: str, status: str):
        """
        Send order status notification
        """
        title = f'Order {status}'
        message = f'Your order #{order_id[:8]} has been {status}.'
        link = f'/orders/{order_id}'
        return NotificationService.create_notification(user_id, 'order', title, message, link)
    
    @staticmethod
    def notify_payment_status(order_id: str, user_id: str, status: str):
        """
        Send payment status notification
        """
        title = f'Payment {status}'
        message = f'Payment for order #{order_id[:8]} is {status}.'
        link = f'/orders/{order_id}'
        return NotificationService.create_notification(user_id, 'payment', title, message, link)
