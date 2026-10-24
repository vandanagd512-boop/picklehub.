from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from functools import wraps

seller_bp = Blueprint('seller', __name__)

def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_seller() and not current_user.is_admin()):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Seller access required. Please switch to Seller role.'}), 403
            flash('Access denied. Seller access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    # If admin, fetch all store orders & products so admin can also test/manage seller orders
    if current_user.is_admin():
        products_result = ProductService.get_all_products(page=1, per_page=10)
        orders_result = OrderService.get_all_orders(page=1, per_page=20)
    else:
        products_result = ProductService.get_products_by_seller(current_user.id, page=1, per_page=10)
        orders_result = OrderService.get_seller_orders(current_user.id, page=1, per_page=20)
    
    # Calculate stats
    total_products = products_result['total']
    total_orders = orders_result['total']
    total_revenue = sum(order.total_amount for order in orders_result['orders'])
    
    # Get low stock products
    low_stock = [p for p in products_result['products'] if p.stock < 10]
    
    # Identify pending incoming orders that need immediate seller action
    pending_orders = [o for o in orders_result['orders'] if (o.status.value if hasattr(o.status, 'value') else str(o.status)).lower() == 'pending']
    
    return render_template('seller/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         low_stock=low_stock,
                         recent_orders=orders_result['orders'][:8],
                         pending_orders=pending_orders,
                         pending_count=len(pending_orders))

@seller_bp.route('/products')
@login_required
@seller_required
def products():
    page = int(request.args.get('page', 1))
    result = ProductService.get_products_by_seller(current_user.id, page=page)
    return render_template('seller/products.html', products=result['products'], total=result['total'], page=result['page'])

@seller_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@login_required
@seller_required
def edit_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    
    if not product or product.seller_id != current_user.id:
        flash('Product not found', 'error')
        return redirect(url_for('seller.products'))
    
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'stock': int(request.form.get('stock')),
            'status': request.form.get('status'),
            'ingredients': request.form.get('ingredients'),
            'spice_level': request.form.get('spice_level'),
            'shelf_life': request.form.get('shelf_life'),
            'weight': request.form.get('weight')
        }
        
        result = ProductService.update_product(product_id, data)
        
        if result['success']:
            flash('Product updated successfully', 'success')
            return redirect(url_for('seller.products'))
        else:
            flash(result['message'], 'error')
    
    from app.services.category_service import CategoryService
    categories = CategoryService.get_all_categories(active_only=True)
    
    return render_template('seller/edit_product.html', product=product, categories=categories)

@seller_bp.route('/products/<product_id>/delete', methods=['POST'])
@login_required
@seller_required
def delete_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    
    if not product or product.seller_id != current_user.id:
        flash('Product not found', 'error')
        return redirect(url_for('seller.products'))
    
    result = ProductService.delete_product(product_id)
    
    if result['success']:
        flash('Product deleted successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('seller.products'))

@seller_bp.route('/orders')
@login_required
@seller_required
def orders():
    page = int(request.args.get('page', 1))
    status_filter = request.args.get('status', 'all').lower()
    
    if current_user.is_admin():
        result = OrderService.get_all_orders(page=page, per_page=50)
    else:
        result = OrderService.get_seller_orders(current_user.id, page=page, per_page=50)
    
    all_orders = result['orders']
    
    def get_st(o):
        return (o.status.value if hasattr(o.status, 'value') else str(o.status)).lower()
        
    pending_orders = [o for o in all_orders if get_st(o) == 'pending']
    confirmed_orders = [o for o in all_orders if get_st(o) == 'confirmed']
    processing_orders = [o for o in all_orders if get_st(o) == 'processing']
    shipped_orders = [o for o in all_orders if get_st(o) == 'shipped']
    delivered_orders = [o for o in all_orders if get_st(o) == 'delivered']
    
    filtered_orders = all_orders
    if status_filter != 'all':
        filtered_orders = [o for o in all_orders if get_st(o) == status_filter]
        
    return render_template('seller/orders.html',
                           orders=filtered_orders,
                           all_orders=all_orders,
                           pending_orders=pending_orders,
                           pending_count=len(pending_orders),
                           confirmed_count=len(confirmed_orders),
                           processing_count=len(processing_orders),
                           shipped_count=len(shipped_orders),
                           delivered_count=len(delivered_orders),
                           current_filter=status_filter,
                           total=result['total'],
                           page=result['page'],
                           per_page=50)

@seller_bp.route('/orders/<order_id>/accept', methods=['GET', 'POST'])
@login_required
@seller_required
def accept_order(order_id):
    result = OrderService.update_order_status(order_id, 'confirmed')
    if result['success']:
        try:
            from app.services.notification_service import NotificationService
            order = OrderService.get_order_by_id(order_id)
            if order:
                NotificationService.notify_order_status(order_id, order.user_id, 'confirmed')
        except Exception:
            pass
        flash(f'Order #{order_id[:8]} accepted & confirmed by kitchen!', 'success')
    else:
        flash(result.get('message', 'Failed to accept order'), 'error')
    return redirect(request.referrer or url_for('seller.orders'))

@seller_bp.route('/orders/<order_id>/pack', methods=['GET', 'POST'])
@login_required
@seller_required
def pack_order(order_id):
    result = OrderService.update_order_status(order_id, 'processing')
    if result['success']:
        try:
            from app.services.notification_service import NotificationService
            order = OrderService.get_order_by_id(order_id)
            if order:
                NotificationService.notify_order_status(order_id, order.user_id, 'processing')
        except Exception:
            pass
        flash(f'Order #{order_id[:8]} marked as Freshly Packed in Martaban!', 'success')
    else:
        flash(result.get('message', 'Failed to update order'), 'error')
    return redirect(request.referrer or url_for('seller.orders'))

@seller_bp.route('/orders/<order_id>/dispatch', methods=['GET', 'POST'])
@login_required
@seller_required
def dispatch_order(order_id):
    courier_name = (request.values.get('courier_name') or 'BlueDart Express').strip()
    tracking_awb = (request.values.get('tracking_awb') or f'AWB{order_id[:6].upper()}').strip()
    estimated_delivery = (request.values.get('estimated_delivery') or '').strip()
    
    order = OrderService.get_order_by_id(order_id)
    if order:
        from app.models.db import db
        eta_part = f" | ETA: {estimated_delivery}" if estimated_delivery else ""
        dispatch_tag = f"[Dispatch: {courier_name} | AWB: {tracking_awb}{eta_part}]"
        order.notes = (order.notes + ' ' if order.notes else '') + dispatch_tag
        db.session.commit()
        
    result = OrderService.update_order_status(order_id, 'shipped')
    if result['success']:
        try:
            from app.services.notification_service import NotificationService
            if order:
                NotificationService.notify_order_status(order_id, order.user_id, 'shipped')
        except Exception:
            pass
        eta_msg = f" (ETA: {estimated_delivery})" if estimated_delivery else ""
        flash(f'Order #{order_id[:8]} dispatched via {courier_name} (Tracking: {tracking_awb}){eta_msg}!', 'success')
    else:
        flash(result.get('message', 'Failed to dispatch order'), 'error')
    return redirect(request.referrer or url_for('seller.orders'))

@seller_bp.route('/orders/<order_id>/deliver', methods=['GET', 'POST'])
@login_required
@seller_required
def deliver_order(order_id):
    result = OrderService.update_order_status(order_id, 'delivered')
    if result['success']:
        try:
            from app.services.notification_service import NotificationService
            order = OrderService.get_order_by_id(order_id)
            if order:
                NotificationService.notify_order_status(order_id, order.user_id, 'delivered')
        except Exception:
            pass
        flash(f'Order #{order_id[:8]} marked as Delivered successfully!', 'success')
    else:
        flash(result.get('message', 'Failed to update order'), 'error')
    return redirect(request.referrer or url_for('seller.orders'))

@seller_bp.route('/orders/<order_id>/update-status', methods=['POST'])
@login_required
@seller_required
def update_order_status(order_id):
    # Support both JSON payload and Form submission
    if request.is_json:
        data = request.get_json() or {}
        status = data.get('status')
        courier_name = (data.get('courier_name') or '').strip()
        tracking_awb = (data.get('tracking_awb') or '').strip()
        estimated_delivery = (data.get('estimated_delivery') or '').strip()
    else:
        status = request.form.get('status')
        courier_name = request.form.get('courier_name', '').strip()
        tracking_awb = request.form.get('tracking_awb', '').strip()
        estimated_delivery = request.form.get('estimated_delivery', '').strip()
    
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    order = OrderService.get_order_by_id(order_id)
    if not order:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        flash('Order not found', 'error')
        return redirect(url_for('seller.orders'))
    
    if courier_name or tracking_awb or estimated_delivery:
        from app.models.db import db
        eta_part = f" | ETA: {estimated_delivery}" if estimated_delivery else ""
        dispatch_tag = f"[Dispatch: {courier_name or 'BlueDart Express'} | AWB: {tracking_awb or 'PENDING'}{eta_part}]"
        order.notes = (order.notes + ' ' if order.notes else '') + dispatch_tag
        db.session.commit()
    
    result = OrderService.update_order_status(order_id, status)
    
    if result['success']:
        try:
            from app.services.notification_service import NotificationService
            NotificationService.notify_order_status(order_id, order.user_id, status)
        except Exception:
            pass
        
        status_label = {
            'pending': 'Pending',
            'confirmed': 'Confirmed (Preparing)',
            'processing': 'Freshly Packed',
            'shipped': 'Dispatched & In Transit',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled'
        }.get(status, status.capitalize())
        
        msg = f'Order #{order_id[:8]} updated to {status_label} successfully!'
        
        if is_ajax:
            return jsonify({
                'success': True,
                'message': msg,
                'order_id': order_id,
                'status': status,
                'status_label': status_label
            })
            
        flash(msg, 'success')
    else:
        err_msg = result.get('message', 'Failed to update status')
        if is_ajax:
            return jsonify({'success': False, 'message': err_msg}), 400
        flash(err_msg, 'error')
    
    return redirect(url_for('seller.orders'))
