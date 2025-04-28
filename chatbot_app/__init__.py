"""
Chatbot Application Package

This package provides a Flask-based chatbot application with emotion detection.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """
    Create and configure the Flask application.

    Args:
        config_name: The configuration to use (default, development, testing, production)

    Returns:
        The configured Flask application
    """
    from chatbot_app.config import config

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure static folders exist
    for folder in ['static', 'static/images', 'static/alcohol']:
        folder_path = os.path.join(os.path.dirname(__file__), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Ensure templates folder exists
    templates_folder = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_folder):
        os.makedirs(templates_folder)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Register blueprints
    with app.app_context():
        # Import routes here to avoid circular imports
        from chatbot_app.routes import main_bp
        app.register_blueprint(main_bp)

    # Register error handlers
    from chatbot_app.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
