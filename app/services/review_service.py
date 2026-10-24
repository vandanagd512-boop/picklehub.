from app.models.db import db
from app.models.review import Review
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class ReviewService:
    
    @staticmethod
    def create_review(data: Dict) -> Dict:
        """
        Create a new review or update existing review
        """
        try:
            # Check if user already reviewed this product
            existing = Review.query.filter_by(
                user_id=data['user_id'],
                product_id=data['product_id']
            ).first()
            
            if existing:
                existing.rating = data['rating']
                existing.comment = data.get('comment', existing.comment)
                db.session.commit()
                review = existing
            else:
                review = Review(
                    id=str(uuid.uuid4()),
                    user_id=data['user_id'],
                    product_id=data['product_id'],
                    rating=data['rating'],
                    comment=data.get('comment'),
                    is_verified_purchase=data.get('is_verified_purchase', False),
                    is_approved=data.get('is_approved', True)
                )
                db.session.add(review)
                db.session.commit()
            
            # Update product rating
            from app.services.product_service import ProductService
            ProductService.update_rating(data['product_id'])
            
            return {
                'success': True,
                'message': 'Review submitted successfully',
                'review': review
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create review error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_review_by_id(review_id: str) -> Optional[Review]:
        """
        Get review by ID
        """
        try:
            return Review.query.get(review_id)
        except Exception as e:
            logger.error(f"Get review error: {str(e)}")
        return None
    
    @staticmethod
    def get_product_reviews(product_id: str, page: int = 1, per_page: int = 10) -> List[Review]:
        """
        Get reviews for a product
        """
        try:
            pagination = Review.query.filter_by(
                product_id=product_id, 
                is_approved=True
            ).order_by(Review.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            return pagination.items
        except Exception as e:
            logger.error(f"Get product reviews error: {str(e)}")
            return []
    
    @staticmethod
    def get_user_reviews(user_id: str, page: int = 1, per_page: int = 10) -> List[Review]:
        """
        Get reviews by user
        """
        try:
            pagination = Review.query.filter_by(user_id=user_id).order_by(
                Review.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            return pagination.items
        except Exception as e:
            logger.error(f"Get user reviews error: {str(e)}")
            return []
    
    @staticmethod
    def update_review(review_id: str, data: Dict) -> Dict:
        """
        Update review
        """
        try:
            review = Review.query.get(review_id)
            if not review:
                return {
                    'success': False,
                    'message': 'Review not found'
                }
            
            for key, value in data.items():
                if hasattr(review, key):
                    setattr(review, key, value)
            
            db.session.commit()
            
            # Update product rating
            from app.services.product_service import ProductService
            ProductService.update_rating(review.product_id)
            
            return {
                'success': True,
                'message': 'Review updated successfully',
                'review': review
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update review error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def delete_review(review_id: str) -> Dict:
        """
        Delete review
        """
        try:
            review = Review.query.get(review_id)
            if review:
                product_id = review.product_id
                
                db.session.delete(review)
                db.session.commit()
                
                # Update product rating
                from app.services.product_service import ProductService
                ProductService.update_rating(product_id)
                
                return {
                    'success': True,
                    'message': 'Review deleted successfully'
                }
            return {
                'success': False,
                'message': 'Review not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete review error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
    
    @staticmethod
    def approve_review(review_id: str) -> Dict:
        """
        Approve review (admin only)
        """
        return ReviewService.update_review(review_id, {'is_approved': True})
    
    @staticmethod
    def get_all_reviews(page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all reviews (admin only)
        """
        try:
            pagination = Review.query.order_by(Review.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'reviews': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            logger.error(f"Get all reviews error: {str(e)}")
            return {'reviews': [], 'total': 0, 'page': page, 'per_page': per_page}
