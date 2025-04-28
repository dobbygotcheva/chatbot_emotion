#!/usr/bin/env python3
"""
Entry point for the Chatbot Application.
Run this script to start the application.
Compatible with Python 3.13 and earlier versions.
"""

import os
import sys
import socket
import ssl
import subprocess
from pathlib import Path

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Check Python version
if sys.version_info.major == 3 and sys.version_info.minor >= 13:
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected. Using compatibility mode.")

# NOTE: For remote access, consider using a cloud hosting service.
# See the README.md file for deployment instructions.

try:
    from chatbot_app import create_app, db

    def get_local_ip():
        """Get the local IP address of the machine."""
        try:
            # Create a socket connection to an external server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't need to be reachable, just used to determine interface
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "your-ip-address"

    def ensure_ssl_certificates():
        """Ensure SSL certificates exist, generate if they don't."""
        cert_dir = Path("ssl_certs")
        cert_path = cert_dir / "cert.pem"
        key_path = cert_dir / "key.pem"

        # If certificates already exist, return their paths
        if cert_path.exists() and key_path.exists():
            return cert_path, key_path

        # Create directory if it doesn't exist
        cert_dir.mkdir(exist_ok=True)

        # Generate self-signed certificate
        print("Generating self-signed SSL certificates...")
        try:
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
                '-out', str(cert_path), '-keyout', str(key_path),
                '-days', '365', '-subj', '/CN=localhost'
            ], check=True)
            print(f"SSL certificates generated at {cert_dir}")
            return cert_path, key_path
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Failed to generate SSL certificates: {e}")
            print("HTTPS will not be available. Install OpenSSL to enable HTTPS.")
            return None, None

    def main():
        """Run the application."""
        # Get environment from environment variable or use development by default
        env = os.getenv('FLASK_ENV', 'development')
        app = create_app(env)

        with app.app_context():
            db.create_all()

        port = int(os.getenv('PORT', 8081))
        local_ip = get_local_ip()

        # Generate or get SSL certificates
        cert_path, key_path = ensure_ssl_certificates()
        # Force HTTP usage regardless of SSL certificate availability
        use_https = False

        # Protocol prefix based on SSL availability
        protocol = "http"

        print(f"\n=== CHATBOT SERVER ADDRESS ===")
        print(f"Starting server on {protocol}://0.0.0.0:{port}")
        print(f"You can access the application at:")
        print(f"  - Local: {protocol}://localhost:{port}")
        print(f"  - Network: {protocol}://{local_ip}:{port} (for other computers on the same network)")
        print(f"  - For remote access, deploy to a cloud hosting service.")
        print(f"  - See README.md for deployment instructions.")
        print(f"===============================\n")

        # Run the app with SSL if certificates are available
        try:
            if use_https:
                ssl_context = (cert_path, key_path)
                app.run(host='0.0.0.0', port=port, debug=(env == 'development'), 
                       use_reloader=False, ssl_context=ssl_context)
            else:
                app.run(host='0.0.0.0', port=port, debug=(env == 'development'), 
                       use_reloader=False)
        except TypeError as e:
            # Handle potential parameter changes in Python 3.13
            print(f"Warning: Flask app.run() parameter error: {e}")
            print("Trying alternative method for Python 3.13 compatibility...")

            # Try with minimal parameters
            if use_https:
                ssl_context = (cert_path, key_path)
                app.run(host='0.0.0.0', port=port, ssl_context=ssl_context)
            else:
                app.run(host='0.0.0.0', port=port)

    if __name__ == "__main__":
        print("Starting the chatbot application...")
        main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
