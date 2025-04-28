"""
Main entry point for the Chatbot Application when run as a module.

This module provides a simple entry point that creates and runs the Flask application.
Compatible with Python 3.13 and earlier versions.
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check Python version
if sys.version_info.major == 3 and sys.version_info.minor >= 13:
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected. Using compatibility mode.")

# NOTE: For remote access, use Render.com (recommended).
# For deployment instructions, see the README.md file.

# Add the project root directory to sys.path if running as a module
if __package__ is None and not hasattr(sys, 'frozen'):
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

try:
    from chatbot_app import create_app, db

    def main():
        """Run the application."""
        # Get environment from environment variable or use development by default
        env = os.getenv('FLASK_ENV', 'development')
        
        try:
            app = create_app(env)
            
            with app.app_context():
                db.create_all()

            port = int(os.getenv('PORT', 8081))

            # Always use HTTP protocol
            protocol = "http"

            # Get local IP address
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            print(f"\n=== CHATBOT SERVER ADDRESS ===")
            print(f"Starting server on {protocol}://0.0.0.0:{port}")
            print(f"You can access the application at:")
            print(f"  - Local: {protocol}://localhost:{port}")
            print(f"  - Network: {protocol}://{local_ip}:{port} (for other computers on the same network)")
            print(f"  - For remote access, deploy to Render.com (recommended).")
            print(f"  - See README.md for deployment instructions.")
            print(f"===============================\n")

            try:
                app.run(host='0.0.0.0', port=port, debug=(env == 'development'), use_reloader=False)
            except TypeError as e:
                # Handle potential parameter changes in Python 3.13
                print(f"Warning: Flask app.run() parameter error: {e}")
                print("Trying alternative method for Python 3.13 compatibility...")

                # Try with minimal parameters
                app.run(host='0.0.0.0', port=port)
        except ImportError as e:
            print(f"Error importing Flask modules: {e}")
            print("This may be caused by an incompatible Flask version.")
            print("Try reinstalling the dependencies with: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"Error starting application: {e}")
            traceback.print_exc()
            sys.exit(1)

    if __name__ == '__main__':
        main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("This may be caused by an incompatible Flask version with Python 3.13.")
    print("Try installing a compatible version with: pip install 'flask==2.2.5'")
    print("Then reinstall all dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)