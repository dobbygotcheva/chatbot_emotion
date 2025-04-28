"""
Configuration settings for the Chatbot Application.

This module contains configuration classes for different environments.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False  # Preserve JSON response order
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Limit payload to 1MB
    
    # Static and template folder paths
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chatbot_app', 'static')
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chatbot_app', 'templates')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    # In production, use a proper secret key
    SECRET_KEY = os.getenv('SECRET_KEY')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}