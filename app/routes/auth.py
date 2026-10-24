from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.address_service import AddressService
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'customer')
        phone = request.form.get('phone')
        
        if not email or not password or not full_name:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        result = AuthService.register(email, password, full_name, role, phone)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        result = AuthService.login(email, password)
        
        if result['success']:
            user = result['user']
            login_user(user)
            
            # Redirect based on next param or role
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/cart/count') and not next_page.startswith('/api'):
                return redirect(next_page)
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_seller():
                return redirect(url_for('seller.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/demo-switch/<role>', methods=['GET', 'POST'])
def demo_switch(role):
    role = (role or '').lower()
    email_map = {
        'customer': 'customer@picklehub.com',
        'seller': 'seller@picklehub.com',
        'admin': 'admin@picklehub.com'
    }
    target_email = email_map.get(role)
    if not target_email:
        flash('Invalid demo role selected', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(email=target_email).first()
    if user:
        login_user(user)
        flash(f'Switched to {user.role.capitalize()} account ({user.full_name})', 'success')
        if user.is_seller():
            return redirect(url_for('seller.orders'))
        elif user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('orders.list'))
            
    flash(f'Demo user for {role} not found', 'error')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_address':
            new_full_name = request.form.get('full_name')
            new_phone = request.form.get('phone')
            new_address_line1 = request.form.get('address_line1')
            new_address_line2 = request.form.get('address_line2')
            new_city = request.form.get('city')
            new_state = request.form.get('state')
            new_postal_code = request.form.get('postal_code')
            new_address_type = request.form.get('address_type', 'home')
            is_default = request.form.get('is_default') == 'on'
            
            res = AddressService.create_address({
                'user_id': current_user.id,
                'full_name': new_full_name,
                'phone': new_phone or current_user.phone or '9999999999',
                'address_line1': new_address_line1,
                'address_line2': new_address_line2,
                'city': new_city,
                'state': new_state,
                'postal_code': new_postal_code,
                'address_type': new_address_type,
                'is_default': is_default
            })
            if res['success']:
                flash('Delivery address added successfully!', 'success')
            else:
                flash(res.get('message', 'Failed to save address.'), 'error')
            return redirect(url_for('auth.profile'))
            
        elif action == 'delete_address':
            address_id = request.form.get('address_id')
            AddressService.delete_address(address_id)
            flash('Address removed successfully.', 'success')
            return redirect(url_for('auth.profile'))
            
        elif action == 'set_default_address':
            address_id = request.form.get('address_id')
            AddressService.set_default_address(address_id)
            flash('Default address updated.', 'success')
            return redirect(url_for('auth.profile'))
            
        else:
            full_name = request.form.get('full_name')
            phone = request.form.get('phone')
            
            result = UserService.update_user(current_user.id, {
                'full_name': full_name,
                'phone': phone
            })
            
            if result['success']:
                flash('Profile updated successfully', 'success')
                current_user.full_name = full_name
                current_user.phone = phone
            else:
                flash(result['message'], 'error')
    
    addresses = AddressService.get_user_addresses(current_user.id)
    return render_template('auth/profile.html', user=current_user, addresses=addresses)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        result = AuthService.reset_password(email)
        
        if result['success']:
            flash('Password reset email sent', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        result = AuthService.update_password(new_password)
        
        if result['success']:
            flash('Password updated successfully', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/reset_password.html', token=token)
