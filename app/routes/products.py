from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.product_service import ProductService
from app.services.review_service import ReviewService
from app.services.wishlist_service import WishlistService
from app.services.ai_service import AIService
from app.services.category_service import CategoryService
from app.services.seed_service import seed_products_if_empty
from werkzeug.utils import secure_filename
import os
from app.config import Config

products_bp = Blueprint('products', __name__)

# ---------------------------------------------------------------------------
# Products listing page  –  /products/
# ---------------------------------------------------------------------------
@products_bp.route('/')
def list_products():
    # Seed sample data on first visit if the table is empty
    seed_products_if_empty()

    query   = request.args.get('q', '').strip()
    page    = max(1, int(request.args.get('page', 1)))
    sort_by = request.args.get('sort', 'newest')

    filters = {
        'category_id': request.args.get('category') or None,
        'min_price':   request.args.get('min_price') or None,
        'max_price':   request.args.get('max_price') or None,
        'spice_level': request.args.get('spice_level') or None,
        'min_rating':  request.args.get('min_rating') or None,
    }
    # Drop empty filters so ProductService doesn't choke on empty strings
    filters = {k: v for k, v in filters.items() if v is not None}
    if sort_by:
        filters['sort_by'] = sort_by

    result     = ProductService.search_products(query, filters, page=page, per_page=12)
    categories = CategoryService.get_all_categories(active_only=True)

    # Wishlist set for the current user (to pre-fill heart icons)
    wishlist_ids = set()
    if current_user.is_authenticated:
        wl = WishlistService.get_user_wishlist(current_user.id)
        wishlist_ids = {item.product_id if hasattr(item, 'product_id') else item['product_id'] for item in wl}

    total_pages = max(1, (result['total'] + result['per_page'] - 1) // result['per_page'])

    return render_template(
        'products/list.html',
        products    = result['products'],
        total       = result['total'],
        page        = result['page'],
        per_page    = result['per_page'],
        total_pages = total_pages,
        query       = query,
        sort_by     = sort_by,
        filters     = filters,
        categories  = categories,
        wishlist_ids= wishlist_ids,
    )

@products_bp.route('/<product_id>')
def detail(product_id):
    product = ProductService.get_product_by_id(product_id)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get reviews
    reviews = ReviewService.get_product_reviews(product_id, page=1, per_page=10)
    
    # Check if in wishlist
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = WishlistService.is_in_wishlist(current_user.id, product_id)
    
    # Get recipe suggestions
    recipes = AIService.get_recipe_suggestions(product_id)
    
    return render_template('products/detail.html',
                         product=product,
                         reviews=reviews,
                         in_wishlist=in_wishlist,
                         recipes=recipes)

@products_bp.route('/<product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    
    result = ReviewService.create_review({
        'user_id': current_user.id,
        'product_id': product_id,
        'rating': rating,
        'comment': comment
    })
    
    if result['success']:
        flash('Review added successfully', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('products.detail', product_id=product_id))

@products_bp.route('/<product_id>/wishlist', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    in_wishlist = WishlistService.is_in_wishlist(current_user.id, product_id)
    
    if in_wishlist:
        result = WishlistService.remove_from_wishlist(current_user.id, product_id)
        message = 'Removed from wishlist'
        added = False
    else:
        result = WishlistService.add_to_wishlist(current_user.id, product_id)
        message = 'Added to wishlist'
        added = True
    
    if request.headers.get('Content-Type') == 'application/json' or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = len(WishlistService.get_user_wishlist(current_user.id))
        return jsonify({'success': result['success'], 'message': message, 'added': added, 'count': count})
    
    flash(message, 'success' if result['success'] else 'error')
    next_url = request.referrer or url_for('products.detail', product_id=product_id)
    return redirect(next_url)

@products_bp.route('/wishlist')
@login_required
def wishlist():
    items = WishlistService.get_user_wishlist(current_user.id)
    return render_template('products/wishlist.html', items=items)

@products_bp.route('/<product_id>/move-to-cart', methods=['POST'])
@login_required
def move_to_cart(product_id):
    from app.services.cart_service import CartService
    quantity = int(request.form.get('quantity', 1))
    CartService.add_to_cart(current_user.id, product_id, quantity)
    WishlistService.remove_from_wishlist(current_user.id, product_id)
    flash('Moved pickle to your cart!', 'success')
    return redirect(url_for('products.wishlist'))

@products_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_seller() and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category_id = request.form.get('category_id')
        stock = int(request.form.get('stock', 0))
        ingredients = request.form.get('ingredients')
        spice_level = request.form.get('spice_level')
        shelf_life = request.form.get('shelf_life')
        weight = request.form.get('weight')
        
        # Handle image uploads
        images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(Config.UPLOAD_FOLDER, 'products', filename)
                    file.save(file_path)
                    images.append(f'/static/uploads/products/{filename}')
        
        result = ProductService.create_product({
            'seller_id': current_user.id,
            'category_id': category_id,
            'name': name,
            'description': description,
            'price': price,
            'stock': stock,
            'images': images,
            'ingredients': ingredients,
            'spice_level': spice_level,
            'shelf_life': shelf_life,
            'weight': weight,
            'status': 'pending' if current_user.is_seller() else 'active'
        })
        
        if result['success']:
            flash('Product created successfully', 'success')
            return redirect(url_for('products.detail', product_id=result['product'].id))
        else:
            flash(result['message'], 'error')
    
    categories = CategoryService.get_all_categories(active_only=True)
    return render_template('products/upload.html', categories=categories)
