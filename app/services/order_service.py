from datetime import datetime
from app.models.db import db
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus, PaymentMethod
from app.models.product import Product
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class OrderService:
    
    @staticmethod
    def create_order(data: Dict) -> Dict:
        """
        Create a new order
        """
        try:
            order = Order(
                id=str(uuid.uuid4()),
                user_id=data['user_id'],
                total_amount=data['total_amount'],
                shipping_address_id=data.get('shipping_address_id'),
                billing_address_id=data.get('billing_address_id'),
                status=OrderStatus(data.get('status', 'pending')),
                payment_status=PaymentStatus(data.get('payment_status', 'pending')),
                payment_method=PaymentMethod(data.get('payment_method', 'cod')),
                payment_id=data.get('payment_id'),
                coupon_code=data.get('coupon_code'),
                discount_amount=data.get('discount_amount', 0),
                shipping_cost=data.get('shipping_cost', 0),
                notes=data.get('notes')
            )
            
            db.session.add(order)
            db.session.flush()
            
            # Add order items
            for item_data in data.get('items', []):
                order_item = OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Order created successfully',
                'order': order
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create order error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Order]:
        """
        Get order by ID
        """
        try:
            return Order.query.get(order_id)
        except Exception as e:
            logger.error(f"Get order error: {str(e)}")
        return None

    @staticmethod
    def get_order_tracking(order_id: str) -> List[Dict]:
        """
        Get tracking timeline for order
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return []
            
            created_str = order.created_at.strftime('%b %d, %Y %I:%M %p') if order.created_at else 'Recently'
            updated_str = order.updated_at.strftime('%b %d, %Y %I:%M %p') if order.updated_at else 'Recently'
            
            status_val = order.status.value if isinstance(order.status, OrderStatus) else str(order.status).lower()
            
            timeline = [
                {
                    'code': 'pending',
                    'status': 'Order Placed',
                    'icon': 'fas fa-receipt',
                    'description': 'Your pickle order has been received and sent to the kitchen.',
                    'timestamp': created_str,
                    'completed': True
                }
            ]
            
            if status_val in ['confirmed', 'processing', 'shipped', 'delivered']:
                timeline.append({
                    'code': 'confirmed',
                    'status': 'Order Confirmed',
                    'icon': 'fas fa-concierge-bell',
                    'description': "Seller kitchen accepted your order! Preparing ingredients & spices.",
                    'timestamp': updated_str,
                    'completed': True
                })
            if status_val in ['processing', 'shipped', 'delivered']:
                timeline.append({
                    'code': 'processing',
                    'status': 'Freshly Packing',
                    'icon': 'fas fa-box-open',
                    'description': 'Pickles are being freshly packed and sealed in airtight Martaban jars.',
                    'timestamp': updated_str,
                    'completed': True
                })
            if status_val in ['shipped', 'delivered']:
                timeline.append({
                    'code': 'shipped',
                    'status': 'Dispatched / In Transit',
                    'icon': 'fas fa-shipping-fast',
                    'description': 'Package handed over to our express courier partner for doorstep delivery.',
                    'timestamp': updated_str,
                    'completed': True
                })
            if status_val == 'delivered':
                timeline.append({
                    'code': 'delivered',
                    'status': 'Delivered',
                    'icon': 'fas fa-smile-beam',
                    'description': 'Order safely delivered to your doorstep. Relish the authentic homemade taste!',
                    'timestamp': updated_str,
                    'completed': True
                })
            elif status_val == 'cancelled':
                timeline.append({
                    'code': 'cancelled',
                    'status': 'Cancelled',
                    'icon': 'fas fa-times-circle',
                    'description': 'This order was cancelled.',
                    'timestamp': updated_str,
                    'completed': True
                })
                
            return timeline
        except Exception as e:
            logger.error(f"Get order tracking error: {str(e)}")
            return []
    
    @staticmethod
    def get_user_orders(user_id: str, page: int = 1, per_page: int = 10) -> Dict:
        """
        Get user's orders with pagination
        """
        try:
            pagination = Order.query.filter_by(user_id=user_id).order_by(
                Order.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'orders': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get user orders error: {str(e)}")
            return {'orders': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_seller_orders(seller_id: str, page: int = 1, per_page: int = 10) -> Dict:
        """
        Get orders for seller's products
        """
        try:
            # Get all orders with items from this seller
            all_orders = Order.query.join(OrderItem).filter(
                OrderItem.product_id.in_(
                    db.session.query(Product.id).filter_by(seller_id=seller_id)
                )
            ).order_by(Order.created_at.desc()).all()
            
            # Simple pagination
            start = (page - 1) * per_page
            paginated_orders = all_orders[start:start + per_page]
            
            return {
                'orders': paginated_orders,
                'total': len(all_orders),
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get seller orders error: {str(e)}")
            return {'orders': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_all_orders(page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all orders (admin only)
        """
        try:
            pagination = Order.query.order_by(Order.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'orders': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get all orders error: {str(e)}")
            return {'orders': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def update_order_status(order_id: str, status: str) -> Dict:
        """
        Update order status
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'message': 'Order not found'
                }
            
            status_clean = str(status).lower().strip()
            if isinstance(status, OrderStatus):
                order.status = status
            else:
                order.status = OrderStatus(status_clean)
            order.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Order status updated successfully',
                'order': order
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update order status error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def update_payment_status(order_id: str, payment_status: str, payment_id: str = None) -> Dict:
        """
        Update payment status
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'message': 'Order not found'
                }
            
            order.payment_status = PaymentStatus(payment_status)
            if payment_id:
                order.payment_id = payment_id
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Payment status updated successfully',
                'order': order
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update payment status error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def cancel_order(order_id: str) -> Dict:
        """
        Cancel order
        """
        return OrderService.update_order_status(order_id, 'cancelled')
    
    @staticmethod
    def get_order_stats(user_id: str = None) -> Dict:
        """
        Get order statistics
        """
        try:
            query = Order.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            orders = query.all()
            
            stats = {
                'total': len(orders),
                'pending': 0,
                'confirmed': 0,
                'processing': 0,
                'shipped': 0,
                'delivered': 0,
                'cancelled': 0
            }
            
            for order in orders:
                status = order.status.value if isinstance(order.status, OrderStatus) else order.status
                if status in stats:
                    stats[status] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Get order stats error: {str(e)}")
            return {'total': 0, 'pending': 0, 'confirmed': 0, 'processing': 0, 'shipped': 0, 'delivered': 0, 'cancelled': 0}
