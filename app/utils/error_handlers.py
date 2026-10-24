from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Forbidden', 'message': str(error)}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Not Found', 'message': str(error)}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong'}), 500
        return render_template('errors/500.html'), 500
