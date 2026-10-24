import re
from flask import request

class Validators:
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate Indian phone number"""
        pattern = r'^[6-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, 'Password must be at least 8 characters long'
        if not re.search(r'[A-Z]', password):
            return False, 'Password must contain at least one uppercase letter'
        if not re.search(r'[a-z]', password):
            return False, 'Password must contain at least one lowercase letter'
        if not re.search(r'\d', password):
            return False, 'Password must contain at least one digit'
        return True, 'Password is valid'
    
    @staticmethod
    def validate_pincode(pincode):
        """Validate Indian pincode"""
        pattern = r'^\d{6}$'
        return re.match(pattern, pincode) is not None
    
    @staticmethod
    def validate_price(price):
        """Validate price"""
        try:
            price_float = float(price)
            return price_float > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_rating(rating):
        """Validate rating (1-5)"""
        try:
            rating_int = int(rating)
            return 1 <= rating_int <= 5
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return ''
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        return text.strip()
    
    @staticmethod
    def validate_image_file(filename):
        """Validate image file extension"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
