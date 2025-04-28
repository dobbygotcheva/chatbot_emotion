"""
Main routes for the Chatbot Application.

This module contains the main routes for the chatbot application.
"""

import os
import sys
import traceback
import logging
from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app

from chatbot_app import db
from chatbot_app.models import ChatbotResponse
from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize chatbot
chatbot = AdvancedChatbot()

@main_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@main_bp.route('/')
def home():
    """Render the home page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Template folder: {current_app.template_folder}")
        logger.error(f"Templates available: {os.listdir(current_app.template_folder) if os.path.exists(current_app.template_folder) else 'Directory not found'}")
        return f"Error loading page: {str(e)}. Please try again.", 500

@main_bp.route('/chat', methods=['POST'])
def chat():
    """Process a chat message and return a response."""
    db_session = None
    try:
        # Input validation
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid JSON format'}), 400

        message = data.get('message', '')

        # Validate message
        if not message:
            return jsonify({'error': 'No message provided'}), 400

        if len(message) > 5000:
            return jsonify({'error': 'Message too long (maximum 5000 characters)'}), 400

        # Process the message and get response
        response = chatbot.process_message(message)

        # Get user IP address for audit (anonymize in production)
        ip_address = request.remote_addr

        # Use a specific session for this request to isolate transactions
        db_session = db.session()

        # Store in database using secure method with transaction
        try:
            # Run diagnostics first to check if database is functioning
            logger.info("Running database pre-checks before saving message")
            try:
                connection_test = ChatbotResponse.test_db_connection()
                if not connection_test['connection_successful']:
                    logger.error(f"Database connection test failed: {connection_test['error']}")
                    raise Exception(f"Database connection test failed: {connection_test['error']}")

                # Log some info about the database
                logger.info(f"Database info: {connection_test['db_info']}")
                if 'table_info' in connection_test and 'has_chatbot_response' in connection_test['table_info']:
                    if not connection_test['table_info']['has_chatbot_response']:
                        logger.warning("Table 'chatbot_response' does not exist. Will create it.")
            except Exception as diag_error:
                logger.error(f"Error running database diagnostics: {diag_error}")
                # Continue anyway

            # Use the compatible method to save to database
            # This handles schema differences and works even if columns are missing
            row_id = ChatbotResponse.save_compatible(
                db_session,
                user_message=message,
                bot_response=response['response'],
                emotion=response['emotion'],
                ip_address=ip_address
            )

            if row_id:
                logger.info(f"Successfully saved chat entry to database with ID: {row_id}")
            else:
                logger.warning("Failed to save chat entry to database using save_compatible method")

        except ValueError as validation_error:
            # Handle validation errors
            if db_session:
                db_session.rollback()
            logger.error(f"Validation error: {validation_error}")

            # Try with sanitized data as fallback using save_compatible
            try:
                from chatbot_app.models import sanitize_text
                sanitized_message = sanitize_text(message)
                sanitized_response = sanitize_text(response['response'])

                # Use save_compatible for the fallback too
                row_id = ChatbotResponse.save_compatible(
                    db_session,
                    user_message=sanitized_message[:500],
                    bot_response=sanitized_response[:500],
                    emotion=response['emotion'][:50] if response['emotion'] else None
                )

                if row_id:
                    logger.info(f"Saved sanitized chat entry to database with ID: {row_id}")
                else:
                    logger.warning("Failed to save sanitized entry using save_compatible")
                    # Continue without database storage
            except Exception as fallback_error:
                logger.error(f"Failed to save sanitized entry: {fallback_error}")
                # Continue without database storage

        except Exception as db_error:
            # Handle other database errors
            if db_session:
                db_session.rollback()
            logger.error(f"Database error: {db_error}")
            logger.error(traceback.format_exc())

            # Try a simplified fallback approach using save_compatible
            try:
                # Minimal record with just the essentials
                truncated_message = message[:100] + "..." if len(message) > 100 else message
                truncated_response = response['response'][:100] + "..." if len(response['response']) > 100 else response['response']

                # Use save_compatible for the final fallback too
                row_id = ChatbotResponse.save_compatible(
                    db_session,
                    user_message=truncated_message,
                    bot_response=truncated_response,
                    emotion="error_fallback"
                )

                if row_id:
                    logger.info(f"Saved minimal fallback chat entry to database with ID: {row_id}")
                else:
                    logger.warning("Failed to save minimal fallback entry using save_compatible")
                    # Continue without database storage
            except Exception as final_error:
                # Final fallback: just continue without storage
                logger.error(f"All database storage attempts failed: {final_error}. Continuing without storage.")

        # Even if db operations fail, still return the response to user
        return jsonify({
            'response': response['response'],
            'emotion': response['emotion'],
            'confidence': response['confidence'],
            'image': response['image'],
            'all_emotions': response.get('all_emotions', {}),
            'hide_emotion': response.get('hide_emotion', False)
        })

    except Exception as e:
        # Handle any other errors
        if db_session:
            db_session.rollback()
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        # Always close the session to prevent connection leaks
        if db_session and db_session is not db.session:
            db_session.close()

# Debug route to check static files
@main_bp.route('/debug/static/<path:filename>')
def debug_static(filename):
    """Debug route to serve static files."""
    return send_from_directory('static', filename)

# Debug route to test emotion mapping
@main_bp.route('/debug/emotions')
def debug_emotions():
    """Debug route to test emotion mapping."""
    # Security check for debug routes
    if not is_authorized_debug_user():
        logger.warning(f"Unauthorized debug access attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized access'}), 403
    try:
        return jsonify({
            'emotions': list(chatbot.emotion_patterns.keys()),
            'emotion_images': chatbot.emotion_images
        })
    except Exception as e:
        logger.error(f"Error in debug_emotions: {e}")
        return jsonify({
            'error': str(e),
            'emotions': [],
            'emotion_images': {}
        }), 500

# Debug route to check app configuration
@main_bp.route('/debug/config')
def debug_config():
    """Debug route to check app configuration."""
    # Security check for debug routes
    if not is_authorized_debug_user():
        logger.warning(f"Unauthorized debug access attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized access'}), 403
    try:
        # Check template and static folder paths
        template_exists = os.path.exists(current_app.template_folder)
        static_exists = os.path.exists(current_app.static_folder)

        # List directories
        template_files = os.listdir(current_app.template_folder) if template_exists else []
        static_files = os.listdir(current_app.static_folder) if static_exists else []

        # Get the current working directory
        cwd = os.getcwd()

        return jsonify({
            'template_folder': current_app.template_folder,
            'template_folder_exists': template_exists,
            'template_files': template_files,
            'static_folder': current_app.static_folder,
            'static_folder_exists': static_exists,
            'static_files': static_files,
            'working_directory': cwd,
            'routes': [str(rule) for rule in current_app.url_map.iter_rules()],
        })
    except Exception as e:
        logger.error(f"Error in debug_config: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

def is_authorized_debug_user():
    """Check if the current request is from an authorized debug user."""
    # In production, use a proper authentication system
    # This is a simple example using environment variables and/or IP restrictions

    # Check for debug token
    debug_token = os.environ.get('DEBUG_ACCESS_TOKEN')
    request_token = request.args.get('token')

    if debug_token and request_token and debug_token == request_token:
        return True

    # Check for debug IPs
    debug_ips = os.environ.get('DEBUG_ALLOWED_IPS', '127.0.0.1,::1').split(',')
    client_ip = request.remote_addr

    if client_ip in debug_ips:
        return True

    # Default to secure (deny)
    return False

@main_bp.route('/debug/diagnostics')
def debug_diagnostics():
    """Comprehensive debug route for database diagnostics."""
    # Security check for debug routes
    if not is_authorized_debug_user():
        logger.warning(f"Unauthorized debug access attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        # Collect comprehensive diagnostic information
        diagnostics = {}

        # App environment info
        diagnostics['environment'] = {
            'flask_env': os.environ.get('FLASK_ENV', 'not set'),
            'debug': current_app.debug,
            'testing': current_app.testing,
            'python_version': sys.version,
            'working_directory': os.getcwd(),
        }

        # Database configuration
        diagnostics['database_config'] = {
            'uri': str(db.engine.url),
            'driver': db.engine.driver,
            'dialect': db.engine.dialect.name,
            'pool_size': getattr(db.engine, 'pool_size', 'unknown'),
        }

        # Test database connection
        diagnostics['connection_test'] = ChatbotResponse.test_db_connection()

        # Check for SQLite specific issues
        if db.engine.dialect.name == 'sqlite':
            # Get SQLite file path from connection URL
            if 'sqlite:///' in str(db.engine.url):
                sqlite_path = str(db.engine.url).replace('sqlite:///', '')
                diagnostics['sqlite'] = {
                    'database_path': sqlite_path,
                    'path_exists': os.path.exists(sqlite_path),
                    'path_is_writable': os.access(os.path.dirname(sqlite_path), os.W_OK) if os.path.exists(os.path.dirname(sqlite_path)) else False,
                    'database_dir': os.path.dirname(sqlite_path),
                    'database_size': os.path.getsize(sqlite_path) if os.path.exists(sqlite_path) else 'file not found',
                }

                # Test direct SQLite connection
                try:
                    import sqlite3
                    conn = sqlite3.connect(sqlite_path)
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check;")
                    result = cursor.fetchone()
                    diagnostics['sqlite']['integrity_check'] = result[0] if result else "No result"
                    conn.close()
                    diagnostics['sqlite']['direct_connection'] = "Success"
                except Exception as e:
                    diagnostics['sqlite']['direct_connection_error'] = str(e)

        # Try to create tables
        try:
            db.create_all()
            diagnostics['table_creation'] = "Success"
        except Exception as e:
            diagnostics['table_creation_error'] = str(e)

        # Inspect database schema
        try:
            inspector = db.inspect(db.engine)
            diagnostics['schema'] = {
                'tables': inspector.get_table_names(),
            }

            # Check our table
            if 'chatbot_response' in diagnostics['schema']['tables']:
                diagnostics['schema']['chatbot_response'] = {
                    'columns': [
                        {
                            'name': col['name'],
                            'type': str(col['type']),
                            'nullable': col['nullable'],
                            'default': str(col['default']) if col['default'] is not None else None,
                            'primary_key': col['primary_key']
                        }
                        for col in inspector.get_columns('chatbot_response')
                    ],
                    'pk': inspector.get_pk_constraint('chatbot_response'),
                    'indexes': inspector.get_indexes('chatbot_response')
                }
        except Exception as e:
            diagnostics['schema_error'] = str(e)

        # Test writing to the database
        try:
            # Simple test entry
            test_entry = ChatbotResponse(
                user_message="Database diagnostic test message",
                bot_response="Database diagnostic test response",
                emotion="diagnostic_test"
            )

            # Start fresh session
            session = db.create_scoped_session()
            session.add(test_entry)
            session.flush()  # Try to flush without committing
            diagnostics['write_test_flush'] = "Success"

            # Try to commit
            session.commit()
            diagnostics['write_test_commit'] = "Success"
            diagnostics['write_test_id'] = test_entry.id
            session.close()
        except Exception as e:
            diagnostics['write_test_error'] = str(e)
            diagnostics['write_test_traceback'] = traceback.format_exc()

        return jsonify(diagnostics)

    except Exception as e:
        logger.error(f"Error in diagnostics: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/debug/database')
def debug_database():
    """Debug route to check database connection and fix issues."""
    # Security check for debug routes
    if not is_authorized_debug_user():
        logger.warning(f"Unauthorized debug access attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized access'}), 403
    try:
        # Get database info
        db_info = {}
        db_info['engine_url'] = str(db.engine.url)
        db_info['tables'] = db.engine.table_names()

        # Check if our table exists
        table_exists = 'chatbot_response' in db_info['tables']
        db_info['chatbot_response_table_exists'] = table_exists

        # Check if we can interact with the database
        db_test_write_success = False
        db_test_read_success = False

        # Try to write a test record
        test_entry = None
        try:
            test_entry = ChatbotResponse(
                user_message="Database test message",
                bot_response="Database test response",
                emotion="test"
            )
            db.session.add(test_entry)
            db.session.commit()
            db_test_write_success = True
            db_info['write_test'] = 'Success: Test record added'
        except Exception as write_error:
            db_info['write_error'] = str(write_error)
            db_info['write_traceback'] = traceback.format_exc()
            # Try to recreate tables if they don't exist
            try:
                if not table_exists:
                    logger.info("Creating database tables...")
                    db.create_all()
                    db_info['table_creation'] = 'Attempted to create tables'
                    # Try the write again
                    test_entry = ChatbotResponse(
                        user_message="Database test message after table creation",
                        bot_response="Database test response",
                        emotion="test"
                    )
                    db.session.add(test_entry)
                    db.session.commit()
                    db_test_write_success = True
                    db_info['write_retry'] = 'Success: Test record added after table creation'
            except Exception as create_error:
                db_info['table_creation_error'] = str(create_error)

        # Try to read records
        try:
            count = ChatbotResponse.query.count()
            db_test_read_success = True
            db_info['read_test'] = f'Success: Found {count} records'

            # Get the latest records
            if count > 0:
                latest_entries = ChatbotResponse.query.order_by(ChatbotResponse.timestamp.desc()).limit(5).all()
                db_info['latest_entries'] = [
                    {
                        'id': entry.id,
                        'user_message': entry.user_message,
                        'bot_response': entry.bot_response[:50] + '...' if len(entry.bot_response) > 50 else entry.bot_response,
                        'emotion': entry.emotion,
                        'timestamp': entry.timestamp.isoformat() if entry.timestamp else None
                    }
                    for entry in latest_entries
                ]
        except Exception as read_error:
            db_info['read_error'] = str(read_error)
            db_info['read_traceback'] = traceback.format_exc()

        # Overall database status
        db_info['status'] = 'OK' if db_test_write_success and db_test_read_success else 'ERROR'

        return jsonify(db_info)
    except Exception as e:
        logger.error(f"Error in debug_database: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/db/view')
def view_database():
    """Route to view database entries."""
    # Security check for database view
    if not is_authorized_debug_user():
        logger.warning(f"Unauthorized database view attempt from {request.remote_addr}")
        return jsonify({'error': 'Unauthorized access'}), 403
    try:
        # Count records
        count = ChatbotResponse.query.count()

        # Get all entries, most recent first
        entries = ChatbotResponse.query.order_by(ChatbotResponse.timestamp.desc()).all()

        formatted_entries = [
            {
                'id': entry.id,
                'user_message': entry.user_message,
                'bot_response': entry.bot_response,
                'emotion': entry.emotion,
                'timestamp': entry.timestamp.isoformat() if entry.timestamp else None
            }
            for entry in entries
        ]

        return jsonify({
            'count': count,
            'entries': formatted_entries
        })
    except Exception as e:
        logger.error(f"Error viewing database: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
