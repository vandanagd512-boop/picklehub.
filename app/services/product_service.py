from app.models.db import db
from app.models.product import Product, ProductStatus
from app.models.category import Category
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class ProductService:

    @staticmethod
    def create_product(data: Dict) -> Dict:
        """
        Create a new product
        """
        try:
            product = Product(
                id=str(uuid.uuid4()),
                seller_id=data['seller_id'],
                category_id=data['category_id'],
                name=data['name'],
                description=data['description'],
                price=data['price'],
                original_price=data.get('original_price'),
                discount_percentage=data.get('discount_percentage'),
                stock=data.get('stock', 0),
                images=data.get('images', []),
                status=ProductStatus(data.get('status', 'active')),
                ingredients=data.get('ingredients'),
                spice_level=data.get('spice_level'),
                shelf_life=data.get('shelf_life'),
                weight=data.get('weight'),
                is_featured=data.get('is_featured', False),
                rating=data.get('rating', 0.0),
                review_count=data.get('review_count', 0)
            )
            
            db.session.add(product)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Product created successfully',
                'product': product
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create product error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Product]:
        """
        Get product by ID
        """
        try:
            return Product.query.get(product_id)
        except Exception as e:
            logger.error(f"Get product error: {str(e)}")
        return None
    
    @staticmethod
    def get_all_products(status: str = 'active', page: int = 1, per_page: int = 12) -> Dict:
        """
        Get all products with pagination
        """
        try:
            query = Product.query
            
            if status:
                query = query.filter_by(status=ProductStatus(status))
            
            pagination = query.order_by(Product.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'products': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get all products error: {str(e)}")
            return {'products': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_products_by_seller(seller_id: str, page: int = 1, per_page: int = 12) -> Dict:
        """
        Get products by seller
        """
        try:
            pagination = Product.query.filter_by(seller_id=seller_id).order_by(
                Product.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'products': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get seller products error: {str(e)}")
            return {'products': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_products_by_category(category_id: str, page: int = 1, per_page: int = 12) -> Dict:
        """
        Get products by category
        """
        try:
            pagination = Product.query.filter_by(
                category_id=category_id, 
                status=ProductStatus.ACTIVE
            ).order_by(Product.rating.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'products': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get category products error: {str(e)}")
            return {'products': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def search_products(query: str, filters: Dict = None, page: int = 1, per_page: int = 12) -> Dict:
        """
        Search products with filters
        """
        try:
            db_query = Product.query.filter_by(status=ProductStatus.ACTIVE)
            
            # Text search
            if query:
                search_pattern = f'%{query}%'
                db_query = db_query.filter(
                    (Product.name.ilike(search_pattern)) | 
                    (Product.description.ilike(search_pattern))
                )
            
            # Apply filters
            if filters:
                if filters.get('category_id'):
                    db_query = db_query.filter_by(category_id=filters['category_id'])
                if filters.get('min_price'):
                    db_query = db_query.filter(Product.price >= float(filters['min_price']))
                if filters.get('max_price'):
                    db_query = db_query.filter(Product.price <= float(filters['max_price']))
                if filters.get('spice_level'):
                    db_query = db_query.filter_by(spice_level=filters['spice_level'])
                if filters.get('min_rating'):
                    db_query = db_query.filter(Product.rating >= float(filters['min_rating']))
                if filters.get('is_featured'):
                    db_query = db_query.filter_by(is_featured=True)
            
            # Apply sorting
            sort_by = filters.get('sort_by') if filters else None
            if sort_by == 'newest':
                db_query = db_query.order_by(Product.created_at.desc())
            elif sort_by == 'price_asc':
                db_query = db_query.order_by(Product.price.asc())
            elif sort_by == 'price_desc':
                db_query = db_query.order_by(Product.price.desc())
            elif sort_by == 'rating':
                db_query = db_query.order_by(Product.rating.desc())
            elif sort_by == 'popularity':
                db_query = db_query.order_by(Product.review_count.desc())
            else:
                db_query = db_query.order_by(Product.created_at.desc())
            
            pagination = db_query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'products': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Search products error: {str(e)}")
            return {'products': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    @staticmethod
    def get_featured_products(limit: int = 8) -> List[Product]:
        """
        Get featured products
        """
        try:
            return Product.query.filter_by(
                is_featured=True, 
                status=ProductStatus.ACTIVE
            ).order_by(Product.rating.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Get featured products error: {str(e)}")
            return []
    
    @staticmethod
    def update_product(product_id: str, data: Dict) -> Dict:
        """
        Update product
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return {
                    'success': False,
                    'message': 'Product not found'
                }
            
            for key, value in data.items():
                if hasattr(product, key):
                    if key == 'status' and isinstance(value, str):
                        try:
                            value = ProductStatus(value.lower())
                        except ValueError:
                            pass
                    setattr(product, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Product updated successfully',
                'product': product
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update product error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def delete_product(product_id: str) -> Dict:
        """
        Delete product
        """
        try:
            product = Product.query.get(product_id)
            if product:
                db.session.delete(product)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Product deleted successfully'
                }
            return {
                'success': False,
                'message': 'Product not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete product error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
    
    @staticmethod
    def update_stock(product_id: str, quantity: int) -> Dict:
        """
        Update product stock
        """
        try:
            product = Product.query.get(product_id)
            if product:
                new_stock = max(0, product.stock + quantity)
                product.stock = new_stock
                if new_stock == 0:
                    product.status = ProductStatus.OUT_OF_STOCK
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Stock updated successfully'
                }
            return {
                'success': False,
                'message': 'Product not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update stock error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def update_rating(product_id: str) -> Dict:
        """
        Recalculate product rating based on reviews
        """
        try:
            from app.models.review import Review
            reviews = Review.query.filter_by(product_id=product_id).all()
            
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                product = Product.query.get(product_id)
                if product:
                    product.rating = round(avg_rating, 2)
                    product.review_count = len(reviews)
                    db.session.commit()
                    return {
                        'success': True,
                        'message': 'Rating updated successfully'
                    }
            return {
                'success': False,
                'message': 'No reviews found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update rating error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
