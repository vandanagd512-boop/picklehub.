from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route('/upload/product-image', methods=['POST'])
@login_required
def upload_product_image():
    """Upload product image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        product_folder = os.path.join(upload_folder, 'products')
        os.makedirs(product_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(product_folder, unique_filename)
        file.save(filepath)
        
        # Return the URL
        file_url = f"/uploads/products/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'url': file_url,
            'filename': unique_filename
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@uploads_bp.route('/uploads/products/<filename>')
def serve_product_image(filename):
    """Serve uploaded product images"""
    try:
        product_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        return send_from_directory(product_folder, filename)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Image not found'}), 404

@uploads_bp.route('/upload/profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    """Upload user profile image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        profile_folder = os.path.join(upload_folder, 'profiles')
        os.makedirs(profile_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(profile_folder, unique_filename)
        file.save(filepath)
        
        # Return the URL
        file_url = f"/uploads/profiles/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'url': file_url,
            'filename': unique_filename
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@uploads_bp.route('/uploads/profiles/<filename>')
def serve_profile_image(filename):
    """Serve uploaded profile images"""
    try:
        profile_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
        return send_from_directory(profile_folder, filename)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Image not found'}), 404
