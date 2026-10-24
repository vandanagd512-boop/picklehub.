from datetime import datetime, timedelta
from flask import session
import json

class Helpers:
    
    @staticmethod
    def format_currency(amount):
        """Format amount as Indian currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj, format_str='%Y-%m-%d'):
        """Format date object"""
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj)
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_datetime(date_obj):
        """Format datetime object"""
        return Helpers.format_date(date_obj, '%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def time_ago(date_obj):
        """Get human-readable time ago string"""
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj)
        
        now = datetime.utcnow()
        diff = now - date_obj
        
        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'{days} day{"s" if days > 1 else ""} ago'
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f'{weeks} week{"s" if weeks > 1 else ""} ago'
        else:
            return Helpers.format_date(date_obj)
    
    @staticmethod
    def truncate(text, length=100):
        """Truncate text to specified length"""
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    @staticmethod
    def slugify(text):
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def get_pagination_info(total, page, per_page, url):
        """Get pagination information for templates"""
        total_pages = (total + per_page - 1) // per_page
        return {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
    
    @staticmethod
    def calculate_discount_percentage(original_price, discounted_price):
        """Calculate discount percentage"""
        if original_price <= 0:
            return 0
        discount = ((original_price - discounted_price) / original_price) * 100
        return round(discount, 2)
    
    @staticmethod
    def generate_order_id():
        """Generate unique order ID"""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def is_ajax_request():
        """Check if request is AJAX"""
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
