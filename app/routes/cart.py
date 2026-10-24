from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.cart_service import CartService
from app.services.coupon_service import CouponService

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
@login_required
def index():
    cart = CartService.get_cart(current_user.id)
    return render_template('cart/index.html', cart=cart)

@cart_bp.route('/add', methods=['POST'])
@login_required
def add():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    result = CartService.add_to_cart(current_user.id, product_id, quantity)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('cart.index'))

@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove():
    product_id = request.form.get('product_id')
    
    result = CartService.remove_from_cart(current_user.id, product_id)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('cart.index'))

@cart_bp.route('/update', methods=['POST'])
@login_required
def update():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    result = CartService.update_cart_item(current_user.id, product_id, quantity)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('cart.index'))

@cart_bp.route('/buy-now/<product_id>', methods=['GET', 'POST'])
def buy_now(product_id):
    if not current_user.is_authenticated:
        flash('Please login to complete your direct purchase', 'info')
        return redirect(url_for('auth.login', next=url_for('cart.buy_now', product_id=product_id)))
        
    quantity = int(request.form.get('quantity', 1) if request.method == 'POST' else request.args.get('quantity', 1))
    
    # Add product directly to cart
    CartService.add_to_cart(current_user.id, product_id, quantity)
    
    # Redirect immediately straight to checkout for 1-click purchase!
    return redirect(url_for('orders.checkout'))

@cart_bp.route('/clear')
@login_required
def clear():
    result = CartService.clear_cart(current_user.id)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('cart.index'))

@cart_bp.route('/validate-coupon', methods=['POST'])
@login_required
def validate_coupon():
    code = request.form.get('coupon_code')
    cart = CartService.get_cart(current_user.id)
    order_total = cart.get_total() if cart else 0
    
    result = CouponService.validate_coupon(code, order_total)
    res_data = {
        'valid': result.get('valid', False),
        'message': result.get('message', ''),
        'discount': result.get('discount', 0),
        'coupon': result['coupon'].to_dict() if result.get('coupon') else None
    }
    return jsonify(res_data)

@cart_bp.route('/count')
def count():
    if not current_user.is_authenticated:
        return jsonify({'count': 0})
    count = CartService.get_cart_count(current_user.id)
    return jsonify({'count': count})
