"""
Error handlers for the Chatbot Application.

This module contains error handlers for the Flask application.
"""

import traceback
import logging
from flask import jsonify

# Configure logging
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    
    @app.errorhandler(404)
    def page_not_found(error):
        """Handle 404 errors."""
        logger.warning(f"404 error: {error}")
        return jsonify({
            'error': 'Page not found',
            'message': str(error),
            'response': 'I couldn\'t find what you were looking for.',
            'emotion': 'neutral',
            'confidence': 0.0,
            'image': 'neutral.jpg'
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors."""
        logger.error(f"500 error: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'response': 'I encountered an error processing your message. Please try again.',
            'emotion': 'neutral',
            'confidence': 0.0,
            'image': 'neutral.jpg'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions."""
        logger.error(f"Uncaught exception: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'response': 'I encountered an unexpected error. Please try again.',
            'emotion': 'neutral',
            'confidence': 0.0,
            'image': 'neutral.jpg'
        }), 500