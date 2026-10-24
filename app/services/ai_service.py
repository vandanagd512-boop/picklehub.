from app.config import Config
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

class AIService:
    
    @staticmethod
    def get_recommendations(user_id: str, limit: int = 6) -> List[Dict]:
        """
        Get AI-powered product recommendations based on user's browsing and purchase history
        """
        try:
            from app.models.order import Order, OrderItem
            from app.models.wishlist import Wishlist
            from app.models.product import Product
            from app.services.product_service import ProductService
            
            # Get user's order product IDs
            order_items = OrderItem.query.join(Order).filter(Order.user_id == user_id).all()
            product_ids = {item.product_id for item in order_items}
            
            # Get user's wishlist
            wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
            for wl in wishlist_items:
                product_ids.add(wl.product_id)
            
            # Get categories of user's interacted products
            category_ids = set()
            if product_ids:
                products = Product.query.filter(Product.id.in_(list(product_ids))).all()
                for product in products:
                    if product.category_id:
                        category_ids.add(product.category_id)
            
            # Get recommendations from same categories
            recommendations = []
            if category_ids:
                for category_id in category_ids:
                    category_products = ProductService.get_products_by_category(category_id, page=1, per_page=limit)
                    for product in category_products['products']:
                        if product.id not in product_ids and len(recommendations) < limit:
                            recommendations.append(product.to_dict())
            
            # If not enough recommendations, get featured products
            if len(recommendations) < limit:
                featured = ProductService.get_featured_products(limit - len(recommendations))
                for product in featured:
                    if product.id not in product_ids and len(recommendations) < limit:
                        recommendations.append(product.to_dict())
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Get recommendations error: {str(e)}")
            # Fallback to featured products
            from app.services.product_service import ProductService
            featured = ProductService.get_featured_products(limit)
            return [p.to_dict() for p in featured]
    
    @staticmethod
    def get_recipe_suggestions(product_id: str) -> List[Dict]:
        """
        Get AI-powered recipe suggestions based on pickle type
        """
        try:
            from app.models.product import Product
            from app.models.category import Category
            from app.services.product_service import ProductService
            
            product = ProductService.get_product_by_id(product_id)
            if not product:
                return []
            
            category = Category.query.get(product.category_id) if product.category_id else None
            cat_name = category.name.lower() if category else product.name.lower()
            
            # Recipe suggestions based on pickle type
            recipes = []
            
            if 'mango' in cat_name:
                recipes = [
                    {
                        'title': 'Mango Pickle Paratha',
                        'description': 'Spiced flatbread stuffed with mango pickle',
                        'ingredients': ['Wheat flour', 'Mango pickle', 'Oil', 'Salt'],
                        'time': '30 mins',
                        'difficulty': 'Easy'
                    },
                    {
                        'title': 'Pickle Rice',
                        'description': 'South Indian style rice with mango pickle',
                        'ingredients': ['Rice', 'Mango pickle', 'Mustard seeds', 'Curry leaves'],
                        'time': '20 mins',
                        'difficulty': 'Easy'
                    },
                    {
                        'title': 'Pickle Sandwich',
                        'description': 'Quick sandwich with mango pickle spread',
                        'ingredients': ['Bread', 'Mango pickle', 'Butter', 'Onion'],
                        'time': '10 mins',
                        'difficulty': 'Easy'
                    }
                ]
            elif 'lemon' in cat_name:
                recipes = [
                    {
                        'title': 'Lemon Pickle Dal',
                        'description': 'Lentil curry with lemon pickle tempering',
                        'ingredients': ['Toor dal', 'Lemon pickle', 'Turmeric', 'Garlic'],
                        'time': '25 mins',
                        'difficulty': 'Easy'
                    },
                    {
                        'title': 'Pickle Curd Rice',
                        'description': 'Cooling rice with lemon pickle',
                        'ingredients': ['Rice', 'Curd', 'Lemon pickle', 'Mustard seeds'],
                        'time': '15 mins',
                        'difficulty': 'Easy'
                    }
                ]
            elif 'chili' in cat_name or 'chilli' in cat_name:
                recipes = [
                    {
                        'title': 'Chili Pickle Chaat',
                        'description': 'Spicy street food with chili pickle',
                        'ingredients': ['Puffed rice', 'Chili pickle', 'Onion', 'Tomato'],
                        'time': '15 mins',
                        'difficulty': 'Easy'
                    },
                    {
                        'title': 'Spicy Pickle Noodles',
                        'description': 'Indo-Chinese fusion with chili pickle',
                        'ingredients': ['Noodles', 'Chili pickle', 'Vegetables', 'Soy sauce'],
                        'time': '20 mins',
                        'difficulty': 'Medium'
                    }
                ]
            else:
                recipes = [
                    {
                        'title': 'Pickle Wrap',
                        'description': 'Quick wrap with your favorite pickle',
                        'ingredients': ['Roti/Tortilla', 'Pickle', 'Onion', 'Cheese'],
                        'time': '10 mins',
                        'difficulty': 'Easy'
                    },
                    {
                        'title': 'Pickle Dosa',
                        'description': 'South Indian crepe with pickle filling',
                        'ingredients': ['Dosa batter', 'Pickle', 'Coconut chutney'],
                        'time': '25 mins',
                        'difficulty': 'Medium'
                    }
                ]
            
            return recipes
            
        except Exception as e:
            logger.error(f"Get recipe suggestions error: {str(e)}")
            return []
    
    @staticmethod
    def analyze_search_query(query: str) -> Dict:
        """
        Analyze search query to extract intent and filters
        """
        try:
            query_lower = query.lower()
            
            filters = {}
            
            # Detect price range
            if 'under' in query_lower or 'below' in query_lower:
                import re
                numbers = re.findall(r'\d+', query)
                if numbers:
                    filters['max_price'] = int(numbers[0])
            
            # Detect spice level
            if 'spicy' in query_lower or 'hot' in query_lower:
                filters['spice_level'] = 'high'
            elif 'mild' in query_lower:
                filters['spice_level'] = 'low'
            
            # Detect rating
            if 'top rated' in query_lower or 'best' in query_lower:
                filters['min_rating'] = 4.0
            
            return {
                'query': query,
                'filters': filters,
                'intent': 'search'
            }
            
        except Exception as e:
            logger.error(f"Analyze search query error: {str(e)}")
            return {'query': query, 'filters': {}, 'intent': 'search'}
