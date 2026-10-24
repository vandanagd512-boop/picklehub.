from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.order_service import OrderService
from app.services.cart_service import CartService
from app.services.address_service import AddressService
from app.services.coupon_service import CouponService
from app.extensions import razorpay_client
import uuid
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = CartService.get_cart(current_user.id)
    
    if not cart or not cart.items:
        flash('Your cart is empty. Add some delicious pickles first!', 'info')
        return redirect(url_for('main.search'))
    
    addresses = AddressService.get_user_addresses(current_user.id)
    default_address = AddressService.get_default_address(current_user.id)
    
    if request.method == 'POST':
        # Get form data
        shipping_address_id = request.form.get('shipping_address')
        billing_address_id = request.form.get('billing_address')
        same_as_shipping = request.form.get('same_as_shipping') == 'on' or request.form.get('same_as_shipping') == '1'
        payment_method = request.form.get('payment_method', 'cod')
        coupon_code = request.form.get('coupon_code', '').strip().upper()
        notes = request.form.get('notes', '').strip()
        
        # New address fields if user enters a new one
        new_full_name = request.form.get('new_full_name', '').strip()
        new_phone = request.form.get('new_phone', '').strip()
        new_address_line1 = request.form.get('new_address_line1', '').strip()
        new_address_line2 = request.form.get('new_address_line2', '').strip()
        new_city = request.form.get('new_city', '').strip()
        new_state = request.form.get('new_state', '').strip()
        new_postal_code = request.form.get('new_postal_code', '').strip()
        new_address_type = request.form.get('new_address_type', 'home')
        save_address = request.form.get('save_address') == 'on' or len(addresses) == 0
        
        shipping_address = None
        
        # 1. Check if user selected an existing address
        if shipping_address_id and shipping_address_id != 'new':
            shipping_address = AddressService.get_address_by_id(shipping_address_id)
        
        # 2. If new address fields provided (or user had no address)
        if not shipping_address and (new_full_name and new_address_line1 and new_city and new_state and new_postal_code):
            addr_result = AddressService.create_address({
                'user_id': current_user.id,
                'full_name': new_full_name,
                'phone': new_phone or current_user.phone or '9999999999',
                'address_line1': new_address_line1,
                'address_line2': new_address_line2,
                'city': new_city,
                'state': new_state,
                'postal_code': new_postal_code,
                'address_type': new_address_type,
                'is_default': True if not addresses else False
            })
            if addr_result['success']:
                shipping_address = addr_result['address']
            else:
                flash(addr_result.get('message', 'Failed to save shipping address.'), 'error')
                return render_template('orders/checkout.html', cart=cart, addresses=addresses, default_address=default_address)
        
        if not shipping_address:
            flash('Please select an existing delivery address or provide a complete new shipping address.', 'error')
            return render_template('orders/checkout.html', cart=cart, addresses=addresses, default_address=default_address)
        
        # Billing address
        billing_address = shipping_address
        if not same_as_shipping and billing_address_id and billing_address_id != shipping_address.id:
            custom_billing = AddressService.get_address_by_id(billing_address_id)
            if custom_billing:
                billing_address = custom_billing
        
        # Calculate totals
        subtotal = float(cart.get_total())
        discount = 0.0
        
        if coupon_code:
            coupon_result = CouponService.validate_coupon(coupon_code, subtotal)
            if coupon_result.get('valid'):
                discount = float(coupon_result.get('discount', 0.0))
                CouponService.use_coupon(coupon_result['coupon'].id)
            else:
                flash(f"Coupon '{coupon_code}' could not be applied: {coupon_result.get('message', 'Invalid coupon')}", 'warning')
        
        total = max(0.0, subtotal - discount)
        
        # Create order payload
        order_data = {
            'user_id': current_user.id,
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in cart.items],
            'total_amount': total,
            'shipping_address_id': shipping_address.id if shipping_address else None,
            'billing_address_id': billing_address.id if billing_address else None,
            'payment_method': payment_method if payment_method in ['cod', 'razorpay'] else 'cod',
            'coupon_code': coupon_code if coupon_code and discount > 0 else None,
            'discount_amount': discount,
            'shipping_cost': 0.0,
            'notes': notes
        }
        
        if payment_method == 'razorpay':
            try:
                # Check if razorpay is configured
                if razorpay_client and hasattr(razorpay_client, 'order') and getattr(razorpay_client, 'key', None):
                    razorpay_order = razorpay_client.order.create({
                        'amount': int(total * 100),  # paise
                        'currency': 'INR',
                        'receipt': f'order_{uuid.uuid4().hex[:8]}',
                        'payment_capture': '1'
                    })
                    order_data['payment_id'] = razorpay_order['id']
                    result = OrderService.create_order(order_data)
                    if result['success']:
                        return render_template('orders/payment.html',
                                             order=result['order'],
                                             razorpay_order=razorpay_order,
                                             key=razorpay_client.key)
                else:
                    raise Exception("Razorpay API credentials not configured in environment")
            except Exception as e:
                logger.warning(f"Razorpay gateway fallback to simulated completion: {e}")
                # Seamless fallback to COD with friendly notice
                order_data['payment_method'] = 'cod'
                order_data['notes'] = (notes + ' ' if notes else '') + '[Demo Mode Payment]'
                result = OrderService.create_order(order_data)
                if result['success']:
                    CartService.clear_cart(current_user.id)
                    flash('Order placed successfully! (Payment set to Cash on Delivery for development)', 'success')
                    return redirect(url_for('orders.detail', order_id=result['order'].id))
        else:
            # Cash on Delivery order
            result = OrderService.create_order(order_data)
            if result['success']:
                CartService.clear_cart(current_user.id)
                flash('Congratulations! Your pickle order has been placed successfully.', 'success')
                return redirect(url_for('orders.detail', order_id=result['order'].id))
        
        flash(result.get('message', 'Failed to place order. Please try again.'), 'error')
    
    return render_template('orders/checkout.html', cart=cart, addresses=addresses, default_address=default_address)

@orders_bp.route('/payment/success', methods=['POST'])
@login_required
def payment_success():
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')
    
    # Verify payment
    params = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    
    try:
        if razorpay_client and hasattr(razorpay_client, 'utility'):
            razorpay_client.utility.verify_payment_signature(params)
        
        # Update order payment status
        from app.models.order import Order, PaymentStatus, OrderStatus
        from app.models.db import db
        order = Order.query.filter_by(payment_id=razorpay_order_id).first()
        if order:
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.CONFIRMED
            order.payment_id = f"{razorpay_payment_id} ({razorpay_order_id})"
            db.session.commit()
            
            try:
                from app.services.notification_service import NotificationService
                NotificationService.notify_order_status(order.id, order.user_id, 'confirmed')
            except Exception:
                pass
        
        # Clear cart
        CartService.clear_cart(current_user.id)
        
        flash('Payment verified successfully! Grandma is preparing your authentic pickles.', 'success')
        if order:
            return redirect(url_for('orders.detail', order_id=order.id))
        return redirect(url_for('orders.list'))
        
    except Exception as e:
        flash('Payment verification failed', 'error')
        return redirect(url_for('cart.index'))

@orders_bp.route('/')
@login_required
def list():
    page = int(request.args.get('page', 1))
    result = OrderService.get_user_orders(current_user.id, page=page)
    return render_template('orders/list.html', orders=result['orders'], total=result['total'], page=result['page'], per_page=10)

@orders_bp.route('/<order_id>')
@login_required
def detail(order_id):
    order = OrderService.get_order_by_id(order_id)
    
    # Allow the customer who placed the order, any admin, or the seller whose products are in this order
    is_authorized = False
    if order:
        if order.user_id == current_user.id or current_user.is_admin():
            is_authorized = True
        elif current_user.is_seller():
            seller_product_ids = {p.id for p in current_user.products}
            if any(item.product_id in seller_product_ids for item in order.items) or not current_user.products:
                is_authorized = True
    
    if not order or not is_authorized:
        flash('Order not found or access denied', 'error')
        return redirect(url_for('orders.list'))
    
    tracking = OrderService.get_order_tracking(order_id)
    
    courier_name = None
    tracking_awb = None
    custom_eta = None
    if order and order.notes:
        m = re.search(r'\[Dispatch:\s*([^|]+)\|\s*AWB:\s*([^\]|]+)(?:\|\s*ETA:\s*([^\]]+))?\]', order.notes)
        if m:
            courier_name = m.group(1).strip()
            tracking_awb = m.group(2).strip()
            if m.group(3):
                custom_eta = m.group(3).strip()
    
    st = order.status.value if hasattr(order.status, 'value') else str(order.status).lower()
    
    if st == 'delivered':
        eta_title = 'Delivered On'
        eta_icon = 'fa-check-circle'
        eta_color = '#22c55e'
        eta_date = order.updated_at.strftime('%A, %d %b') if order.updated_at else 'Delivered'
        eta_subtext = f'Handed over via {courier_name}' if courier_name else 'Delivered safely to door'
    elif st == 'shipped':
        eta_title = 'Expected Delivery'
        eta_icon = 'fa-truck-fast'
        eta_color = '#3b82f6'
        eta_date = custom_eta or ((order.updated_at or order.created_at) + timedelta(days=2)).strftime('%A, %d %b')
        eta_subtext = f"{courier_name} • {tracking_awb}" if (courier_name and tracking_awb) else (courier_name or 'Express In-Transit')
    elif st == 'processing':
        eta_title = 'Dispatch Window'
        eta_icon = 'fa-box-open'
        eta_color = '#8b5cf6'
        eta_date = 'Freshly Packing'
        eta_subtext = 'Express Handover in 2-4 hrs'
    elif st == 'cancelled':
        eta_title = 'Order Status'
        eta_icon = 'fa-ban'
        eta_color = '#ef4444'
        eta_date = 'Cancelled'
        eta_subtext = 'Refund Processing'
    else:  # pending, confirmed
        eta_title = 'Estimated Delivery'
        eta_icon = 'fa-calendar-check'
        eta_color = 'var(--accent)'
        eta_date = custom_eta or ((order.created_at + timedelta(days=3)).strftime('%A, %d %b') if order.created_at else 'In 2-3 Business Days')
        eta_subtext = 'Standard Kitchen Fulfillment'
    
    return render_template(
        'orders/detail.html',
        order=order,
        tracking=tracking,
        courier_name=courier_name,
        tracking_awb=tracking_awb,
        eta_title=eta_title,
        eta_icon=eta_icon,
        eta_color=eta_color,
        eta_date=eta_date,
        eta_subtext=eta_subtext
    )

@orders_bp.route('/<order_id>/invoice')
@login_required
def invoice(order_id):
    order = OrderService.get_order_by_id(order_id)
    if not order or (order.user_id != current_user.id and not current_user.is_admin() and not current_user.is_seller()):
        flash('Order not found', 'error')
        return redirect(url_for('orders.list'))
    return render_template('orders/invoice.html', order=order)

@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    order = OrderService.get_order_by_id(order_id)
    
    if not order or order.user_id != current_user.id:
        flash('Order not found', 'error')
        return redirect(url_for('orders.list'))
    
    if not order.can_cancel():
        flash('Order cannot be cancelled at this stage.', 'error')
        return redirect(url_for('orders.detail', order_id=order_id))
    
    cancel_reason = request.form.get('cancel_reason', 'Cancelled by customer')
    from app.models.db import db
    order.notes = (order.notes + ' ' if order.notes else '') + f'[Cancellation Reason: {cancel_reason}]'
    result = OrderService.cancel_order(order_id)
    
    if result['success']:
        flash('Your order has been cancelled successfully.', 'success')
    else:
        flash(result.get('message', 'Failed to cancel order.'), 'error')
    
    return redirect(url_for('orders.detail', order_id=order_id))
