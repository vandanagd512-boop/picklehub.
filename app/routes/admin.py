from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.services.category_service import CategoryService
from app.services.coupon_service import CouponService
from app.services.review_service import ReviewService
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get overall stats
    users_result = UserService.get_all_users(page=1, per_page=1)
    products_result = ProductService.get_all_products(page=1, per_page=1)
    orders_result = OrderService.get_all_orders(page=1, per_page=1)
    
    total_users = users_result['total']
    total_products = products_result['total']
    total_orders = orders_result['total']
    
    # Calculate revenue
    all_orders = OrderService.get_all_orders(page=1, per_page=1000)
    total_revenue = sum(order.total_amount for order in all_orders['orders'])
    
    # Get recent orders
    recent_orders = OrderService.get_all_orders(page=1, per_page=10)['orders']
    
    # Get pending products
    pending_products = ProductService.get_all_products(status='pending', page=1, per_page=10)['products']
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         pending_products=pending_products)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = int(request.args.get('page', 1))
    result = UserService.get_all_users(page=page)
    return render_template('admin/users.html', users=result['users'], total=result['total'], page=result['page'])

@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = UserService.get_user_by_id(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
    
    if user.is_active:
        result = UserService.deactivate_user(user_id)
    else:
        result = UserService.activate_user(user_id)
    
    if result['success']:
        flash('User status updated successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    new_role = request.form.get('role')
    result = UserService.change_role(user_id, new_role)
    
    if result['success']:
        flash('User role updated successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = int(request.args.get('page', 1))
    status = request.args.get('status', 'active')
    result = ProductService.get_all_products(status=status, page=page)
    return render_template('admin/products.html', products=result['products'], total=result['total'], page=result['page'], status=status)

@admin_bp.route('/products/<product_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_product(product_id):
    result = ProductService.update_product(product_id, {'status': 'active'})
    
    if result['success']:
        flash('Product approved successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.products', status='pending'))

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    page = int(request.args.get('page', 1))
    result = OrderService.get_all_orders(page=page)
    return render_template('admin/orders.html', orders=result['orders'], total=result['total'], page=result['page'])

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = CategoryService.get_all_categories(active_only=False)
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/create', methods=['POST'])
@login_required
@admin_required
def create_category():
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'sort_order': int(request.form.get('sort_order', 0))
    }
    
    result = CategoryService.create_category(data)
    
    if result['success']:
        flash('Category created successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    result = CategoryService.delete_category(category_id)
    
    if result['success']:
        flash('Category deleted successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    page = int(request.args.get('page', 1))
    result = CouponService.get_all_coupons(active_only=False, page=page)
    return render_template('admin/coupons.html', coupons=result['coupons'], total=result['total'], page=result['page'], per_page=result.get('per_page', 20))

@admin_bp.route('/coupons/create', methods=['POST'])
@login_required
@admin_required
def create_coupon():
    from datetime import datetime, timedelta
    
    data = {
        'code': request.form.get('code').upper(),
        'coupon_type': request.form.get('coupon_type'),
        'value': float(request.form.get('value')),
        'min_order_value': float(request.form.get('min_order_value', 0)),
        'max_discount': float(request.form.get('max_discount')) if request.form.get('max_discount') else None,
        'usage_limit': int(request.form.get('usage_limit')) if request.form.get('usage_limit') else None,
        'valid_from': datetime.utcnow().isoformat(),
        'valid_until': (datetime.utcnow() + timedelta(days=int(request.form.get('valid_days', 30)))).isoformat(),
        'description': request.form.get('description')
    }
    
    result = CouponService.create_coupon(data)
    
    if result['success']:
        flash('Coupon created successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/coupons/<coupon_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_coupon(coupon_id):
    result = CouponService.delete_coupon(coupon_id)
    if result['success']:
        flash('Coupon deleted successfully', 'success')
    else:
        flash(result.get('message', 'Failed to delete coupon'), 'error')
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/coupons/<coupon_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_coupon_status(coupon_id):
    coupon = CouponService.get_coupon_by_id(coupon_id)
    if not coupon:
        flash('Coupon not found', 'error')
        return redirect(url_for('admin.coupons'))
    
    new_status = not coupon.is_active
    result = CouponService.update_coupon(coupon_id, {'is_active': new_status})
    if result['success']:
        flash(f"Coupon '{coupon.code}' is now {'Active' if new_status else 'Inactive'}", 'success')
    else:
        flash('Failed to update coupon status', 'error')
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    page = int(request.args.get('page', 1))
    result = ReviewService.get_all_reviews(page=page)
    return render_template('admin/reviews.html', reviews=result['reviews'], total=result['total'], page=result['page'])

@admin_bp.route('/reviews/<review_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    result = ReviewService.approve_review(review_id)
    
    if result['success']:
        flash('Review approved successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('admin.reviews'))
