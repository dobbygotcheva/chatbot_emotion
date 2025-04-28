"""
Database models for the Chatbot Application.

This module contains SQLAlchemy models for the application with
security features for data validation and integrity.
"""

import re
import traceback
from datetime import datetime
from sqlalchemy.event import listen
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates
import logging

from chatbot_app import db

# Configure logging
logger = logging.getLogger(__name__)

def sanitize_text(text):
    """
    Sanitize text input to prevent SQL injection and XSS attacks.

    Args:
        text (str): Text to sanitize

    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Replace potentially harmful characters
    sanitized = text.replace("<", "&lt;").replace(">", "&gt;")

    # Remove any SQL injection attempts
    sql_patterns = [
        r'(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|UNION|CREATE|WHERE)(\s|$)',
        r'(\s|^)(--)',
        r'(;)',
        r'(/\*.*\*/)'
    ]

    for pattern in sql_patterns:
        sanitized = re.sub(pattern, ' ', sanitized, flags=re.IGNORECASE)

    return sanitized.strip()

class ChatbotResponse(db.Model):
    """Model for storing chatbot responses with validation and sanitization."""

    __tablename__ = 'chatbot_response'

    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # Add IP address for audit purposes (store hashed/anonymized in production)
    ip_address = db.Column(db.String(45), nullable=True)
    # Add a flag for potentially problematic content
    flagged = db.Column(db.Boolean, default=False)

    @validates('user_message')
    def validate_user_message(self, key, message):
        """Validate and sanitize user message."""
        if not message:
            raise ValueError("User message cannot be empty")

        if len(message) > 5000:  # Set a reasonable limit
            message = message[:5000]
            logger.warning(f"User message truncated to 5000 characters")

        return sanitize_text(message)

    @validates('bot_response')
    def validate_bot_response(self, key, response):
        """Validate and sanitize bot response."""
        if not response:
            raise ValueError("Bot response cannot be empty")

        if len(response) > 5000:  # Set a reasonable limit
            response = response[:5000]
            logger.warning(f"Bot response truncated to 5000 characters")

        return sanitize_text(response)

    @validates('emotion')
    def validate_emotion(self, key, emotion):
        """Validate emotion."""
        if emotion and len(emotion) > 50:
            emotion = emotion[:50]

        return sanitize_text(emotion) if emotion else None

    def __repr__(self):
        """String representation of the model."""
        return f"<ChatbotResponse {self.id}: {self.emotion}>"

    @classmethod
    def create_safe(cls, user_message, bot_response, emotion=None, ip_address=None):
        """
        Safely create a new ChatbotResponse instance with validation and sanitization.

        Args:
            user_message (str): The user's message
            bot_response (str): The chatbot's response
            emotion (str, optional): The detected emotion
            ip_address (str, optional): The user's IP address

        Returns:
            ChatbotResponse: A new instance of ChatbotResponse

        Raises:
            ValueError: If validation fails
        """
        # Validate and sanitize inputs
        if not user_message:
            raise ValueError("User message cannot be empty")
        if not bot_response:
            raise ValueError("Bot response cannot be empty")

        # Create a dictionary with the required fields
        data = {
            'user_message': sanitize_text(user_message[:5000]),
            'bot_response': sanitize_text(bot_response[:5000]),
        }

        # Add optional fields if provided
        if emotion:
            data['emotion'] = sanitize_text(emotion[:50])

        # Create the instance with minimal fields
        instance = cls(
            user_message=data['user_message'],
            bot_response=data['bot_response'],
            emotion=data.get('emotion')
        )

        return instance

    @classmethod
    def save_compatible(cls, session, user_message, bot_response, emotion=None, ip_address=None):
        """
        Save a chat response to the database using direct SQL to handle schema differences.

        Args:
            session: SQLAlchemy session
            user_message (str): The user's message
            bot_response (str): The chatbot's response
            emotion (str, optional): The detected emotion
            ip_address (str, optional): The user's IP address

        Returns:
            int: ID of the inserted record or None if failed

        Raises:
            ValueError: If validation fails
        """
        # Validate and sanitize inputs
        if not user_message:
            raise ValueError("User message cannot be empty")
        if not bot_response:
            raise ValueError("Bot response cannot be empty")

        # Sanitize inputs
        user_message = sanitize_text(user_message[:5000])
        bot_response = sanitize_text(bot_response[:5000])
        emotion = sanitize_text(emotion[:50]) if emotion else None

        try:
            # Get the actual columns in the database table
            with session.connection() as conn:
                # Check if table exists
                inspector = db.inspect(conn)
                if not inspector.has_table('chatbot_response'):
                    # Table doesn't exist, create it with minimal columns
                    logger.info("Table 'chatbot_response' doesn't exist. Creating it.")
                    conn.execute(db.text("""
                        CREATE TABLE IF NOT EXISTS chatbot_response (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_message TEXT NOT NULL,
                            bot_response TEXT NOT NULL,
                            emotion VARCHAR(50),
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.commit()

                # Get columns that exist in the table
                columns = [column['name'] for column in inspector.get_columns('chatbot_response')]

                # Build SQL based on existing columns
                fields = ['user_message', 'bot_response']
                values = {'user_message': user_message, 'bot_response': bot_response}

                if 'emotion' in columns and emotion:
                    fields.append('emotion')
                    values['emotion'] = emotion

                if 'ip_address' in columns and ip_address:
                    fields.append('ip_address')
                    values['ip_address'] = ip_address

                if 'timestamp' in columns:
                    from datetime import datetime
                    fields.append('timestamp')
                    values['timestamp'] = datetime.utcnow()

                # Execute the insert
                # Use named parameters in the format :param_name
                placeholders = [f":{field}" for field in fields]
                sql = f"INSERT INTO chatbot_response ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
                result = conn.execute(db.text(sql), values)
                conn.commit()

                # Get the ID of the inserted record
                if result.rowcount > 0:
                    # Get the last inserted ID
                    result = conn.execute(db.text("SELECT last_insert_rowid()"))
                    row_id = result.scalar()
                    logger.info(f"Successfully saved chat entry to database with ID: {row_id}")
                    return row_id
                else:
                    logger.error("Failed to insert record")
                    return None

        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    def test_db_connection():
        """
        Test the database connection and return diagnostic information.

        Returns:
            dict: Diagnostic information about the database
        """
        try:
            result = {
                'connection_successful': False,
                'error': None,
                'db_info': {},
                'table_info': {}
            }

            # Test basic connection
            connection_valid = False
            try:
                # Try to get engine information
                result['db_info']['engine'] = str(db.engine.url)
                result['db_info']['driver'] = db.engine.driver

                # Check if we can execute a simple query
                with db.engine.connect() as conn:
                    conn.execute(db.text("SELECT 1"))
                    connection_valid = True

                result['connection_successful'] = True
            except Exception as e:
                result['error'] = f"Connection error: {str(e)}"
                return result

            # Get table information
            if connection_valid:
                try:
                    # Check if our table exists
                    inspector = db.inspect(db.engine)
                    result['table_info']['tables'] = inspector.get_table_names()

                    our_table = 'chatbot_response'
                    has_table = our_table in result['table_info']['tables']
                    result['table_info']['has_chatbot_response'] = has_table

                    # If our table exists, get column details
                    if has_table:
                        result['table_info']['columns'] = [
                            {
                                'name': column['name'],
                                'type': str(column['type']),
                                'nullable': column['nullable']
                            }
                            for column in inspector.get_columns(our_table)
                        ]
                except Exception as e:
                    result['table_info']['error'] = f"Failed to inspect tables: {str(e)}"

            return result
        except Exception as e:
            return {
                'connection_successful': False,
                'error': f"Unexpected error in test_db_connection: {str(e)}"
            }
