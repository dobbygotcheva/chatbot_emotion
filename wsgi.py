"""
WSGI entry point for the Chatbot Application.
This file is used by Gunicorn to serve the application on Render.com and other WSGI-compatible servers.
"""

import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the application factory
from chatbot_app import create_app, db

# Create the Flask application using the factory
# Use 'production' environment for deployment
app = create_app('production')

# Initialize the database if needed
with app.app_context():
    db.create_all()

# This is the object that will be imported by Gunicorn
# The name 'app' is required - do not change it
# Gunicorn will look for an object called 'app' in this file
if __name__ == "__main__":
    # Only run this when executed directly (not via Gunicorn)
    # For local debugging only
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port)
