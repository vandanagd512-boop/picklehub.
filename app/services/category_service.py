from app.models.db import db
from app.models.category import Category
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class CategoryService:
    
    @staticmethod
    def create_category(data: Dict) -> Dict:
        """
        Create a new category
        """
        try:
            category = Category(
                id=str(uuid.uuid4()),
                name=data['name'],
                description=data.get('description'),
                image=data.get('image'),
                is_active=data.get('is_active', True),
                sort_order=data.get('sort_order', 0)
            )
            
            db.session.add(category)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Category created successfully',
                'category': category
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create category error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[Category]:
        """
        Get category by ID
        """
        try:
            return Category.query.get(category_id)
        except Exception as e:
            logger.error(f"Get category error: {str(e)}")
        return None
    
    @staticmethod
    def get_all_categories(active_only: bool = True) -> List[Category]:
        """
        Get all categories
        """
        try:
            query = Category.query
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(Category.sort_order).all()
        except Exception as e:
            logger.error(f"Get all categories error: {str(e)}")
            return []
    
    @staticmethod
    def update_category(category_id: str, data: Dict) -> Dict:
        """
        Update category
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                return {
                    'success': False,
                    'message': 'Category not found'
                }
            
            for key, value in data.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Category updated successfully',
                'category': category
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update category error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def delete_category(category_id: str) -> Dict:
        """
        Delete category
        """
        try:
            category = Category.query.get(category_id)
            if category:
                db.session.delete(category)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Category deleted successfully'
                }
            return {
                'success': False,
                'message': 'Category not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete category error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
