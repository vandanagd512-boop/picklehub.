from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.cart_service import CartService
from app.services.wishlist_service import WishlistService
from app.services.order_service import OrderService
from app.services.ai_service import AIService
import re
from datetime import timedelta

api_bp = Blueprint('api', __name__)

@api_bp.route('/products')
def get_products():
    page = int(request.args.get('page', 1))
    category_id = request.args.get('category_id')
    query = request.args.get('q')
    
    if query:
        result = ProductService.search_products(query, {}, page=page)
    elif category_id:
        result = ProductService.get_products_by_category(category_id, page=page)
    else:
        result = ProductService.get_all_products(page=page)
    
    return jsonify({
        'products': [p.to_dict() for p in result['products']],
        'total': result['total'],
        'page': result['page']
    })

@api_bp.route('/products/<product_id>')
def get_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({'error': 'Product not found'}), 404

@api_bp.route('/categories')
def get_categories():
    categories = CategoryService.get_all_categories(active_only=True)
    return jsonify([c.to_dict() for c in categories])

@api_bp.route('/cart/count')
def cart_count():
    if not current_user.is_authenticated:
        return jsonify({'count': 0})
    count = CartService.get_cart_count(current_user.id)
    return jsonify({'count': count})

@api_bp.route('/recommendations')
@login_required
def recommendations():
    limit = int(request.args.get('limit', 6))
    recommendations = AIService.get_recommendations(current_user.id, limit)
    return jsonify(recommendations)

@api_bp.route('/recipes/<product_id>')
def recipes(product_id):
    recipes = AIService.get_recipe_suggestions(product_id)
    return jsonify(recipes)

@api_bp.route('/search/analyze')
def analyze_search():
    query = request.args.get('q', '')
    result = AIService.analyze_search_query(query)
    return jsonify(result)

@api_bp.route('/orders/<order_id>/live-status')
@login_required
def order_live_status(order_id):
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
        
    is_owner = (order.user_id == current_user.id)
    is_authorized = is_owner or current_user.is_seller() or current_user.is_admin()
    if not is_authorized:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    status_val = order.status.value if hasattr(order.status, 'value') else str(order.status).lower()
    
    stage_map = {
        'pending': 1,
        'confirmed': 2,
        'processing': 3,
        'shipped': 4,
        'delivered': 5,
        'cancelled': -1,
        'refunded': -2
    }
    
    stage_titles = {
        'pending': 'Order Placed & Awaiting Seller Confirmation',
        'confirmed': 'Order Confirmed by Seller!',
        'processing': 'Freshly Packing in Authentic Martaban',
        'shipped': 'Dispatched & Out for Delivery',
        'delivered': 'Order Safely Delivered!',
        'cancelled': 'Order Cancelled',
        'refunded': 'Order Refunded'
    }
    
    stage_subtitles = {
        'pending': 'We have notified the pickle kitchen. Seller usually confirms within 1-2 minutes.',
        'confirmed': "Grandma's Heritage Kitchen has confirmed your order. Hand-picking raw ingredients & authentic spices.",
        'processing': 'Airtight Martaban sealing & hygienic packing in progress with pure mustard/sesame oil cover.',
        'shipped': 'Package handed over to our express courier partner. Tracking is live!',
        'delivered': 'Delivered! Hope you relish every bite of authentic Indian homemade pickle.',
        'cancelled': 'This order was cancelled.',
        'refunded': 'The refund for this order has been processed.'
    }

    courier_name = None
    tracking_awb = None
    custom_eta = None
    if order.notes:
        m = re.search(r'\[Dispatch:\s*([^|]+)\|\s*AWB:\s*([^\]|]+)(?:\|\s*ETA:\s*([^\]]+))?\]', order.notes)
        if m:
            courier_name = m.group(1).strip()
            tracking_awb = m.group(2).strip()
            if m.group(3):
                custom_eta = m.group(3).strip()

    timeline = OrderService.get_order_tracking(order_id)
    
    if status_val == 'delivered':
        eta_title = 'Delivered On'
        eta_icon = 'fa-check-circle'
        eta_color = '#22c55e'
        eta_str = order.updated_at.strftime('%A, %d %b') if order.updated_at else 'Delivered'
        eta_subtext = f'Handed over via {courier_name}' if courier_name else 'Delivered safely to door'
    elif status_val == 'shipped':
        eta_title = 'Expected Delivery'
        eta_icon = 'fa-truck-fast'
        eta_color = '#3b82f6'
        eta_str = custom_eta or ((order.updated_at or order.created_at) + timedelta(days=2)).strftime('%A, %d %b')
        eta_subtext = f"{courier_name} • {tracking_awb}" if (courier_name and tracking_awb) else (courier_name or 'Express In-Transit')
    elif status_val == 'processing':
        eta_title = 'Dispatch Window'
        eta_icon = 'fa-box-open'
        eta_color = '#8b5cf6'
        eta_str = 'Freshly Packing'
        eta_subtext = 'Express Handover in 2-4 hrs'
    elif status_val == 'cancelled':
        eta_title = 'Order Status'
        eta_icon = 'fa-ban'
        eta_color = '#ef4444'
        eta_str = 'Cancelled'
        eta_subtext = 'Refund Processing'
    else:  # pending, confirmed
        eta_title = 'Estimated Delivery'
        eta_icon = 'fa-calendar-check'
        eta_color = 'var(--accent)'
        eta_str = custom_eta or ((order.created_at + timedelta(days=3)).strftime('%A, %d %b') if order.created_at else 'In 2-3 Business Days')
        eta_subtext = 'Standard Kitchen Fulfillment'
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'short_id': order.id[:8],
        'status': status_val,
        'stage': stage_map.get(status_val, 1),
        'title': stage_titles.get(status_val, status_val.capitalize()),
        'subtitle': stage_subtitles.get(status_val, ''),
        'updated_at': order.updated_at.strftime('%I:%M %p, %d %b %Y') if order.updated_at else 'Just now',
        'courier_name': courier_name,
        'tracking_awb': tracking_awb,
        'eta_title': eta_title,
        'eta_icon': eta_icon,
        'eta_color': eta_color,
        'estimated_delivery': eta_str,
        'eta_subtext': eta_subtext,
        'can_cancel': order.can_cancel(),
        'timeline': timeline
    })

@api_bp.route('/seller/pending-orders-count')
@login_required
def seller_pending_orders_count():
    if not current_user.is_seller() and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.models.order import Order, OrderItem, OrderStatus
    from app.models.product import Product
    from app.models.db import db
    
    pending_count = Order.query.join(OrderItem).filter(
        OrderItem.product_id.in_(
            db.session.query(Product.id).filter_by(seller_id=current_user.id)
        ),
        Order.status == OrderStatus.PENDING
    ).distinct().count()
    
    return jsonify({
        'pending_count': pending_count
    })
