from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.ai_service import AIService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured products
    featured_products = ProductService.get_featured_products(limit=8)
    
    # Get categories
    categories = CategoryService.get_all_categories(active_only=True)
    
    # Get recommendations if user is logged in
    recommendations = []
    if current_user.is_authenticated:
        recommendations = AIService.get_recommendations(current_user.id, limit=4)
    
    return render_template('main/index.html', 
                         featured_products=featured_products,
                         categories=categories,
                         recommendations=recommendations)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort', '')
    
    # Get filters from request
    filters = {
        'category_id': request.args.get('category'),
        'min_price': request.args.get('min_price'),
        'max_price': request.args.get('max_price'),
        'spice_level': request.args.get('spice_level'),
        'min_rating': request.args.get('min_rating'),
        'is_featured': request.args.get('featured') == 'true'
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Add sorting
    if sort_by:
        filters['sort_by'] = sort_by
    
    # Search products
    result = ProductService.search_products(query, filters, page=page)
    
    # Get categories for filter sidebar
    categories = CategoryService.get_all_categories(active_only=True)
    
    return render_template('main/search.html',
                         products=result['products'],
                         total=result['total'],
                         page=result['page'],
                         per_page=result['per_page'],
                         query=query,
                         filters=filters,
                         categories=categories)

@main_bp.route('/category/<category_id>')
def category(category_id):
    page = int(request.args.get('page', 1))
    
    category = CategoryService.get_category_by_id(category_id)
    result = ProductService.get_products_by_category(category_id, page=page)
    
    return render_template('main/category.html',
                         category=category,
                         products=result['products'],
                         total=result['total'],
                         page=result['page'],
                         per_page=result['per_page'])

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', 'Friend')
        flash(f'Thank you, {name}! Your message has been received. Our pickle artisans will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('main/contact.html')

@main_bp.route('/shipping-policy')
def shipping_policy():
    return render_template('main/policy.html', title='Shipping & Delivery Policy', policy_type='shipping')

@main_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('main/policy.html', title='Privacy & Security Policy', policy_type='privacy')

@main_bp.route('/refund-policy')
def refund_policy():
    return render_template('main/policy.html', title='Returns, Replacement & Refund Policy', policy_type='refund')
