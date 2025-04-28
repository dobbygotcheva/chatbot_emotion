import pytest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot

@pytest.fixture
def chatbot():
    return AdvancedChatbot()

def test_chatbot_initialization(chatbot):
    assert chatbot is not None
    assert hasattr(chatbot, 'sentiment_analyzer')
    assert hasattr(chatbot, 'conversation_memory')
    assert hasattr(chatbot, 'context')

def test_process_message(chatbot):
    # Test greeting
    response = chatbot.process_message("Hello")
    assert isinstance(response, dict)
    assert 'response' in response
    assert isinstance(response['response'], str)
    assert len(response['response']) > 0

    # Test emotional message
    response = chatbot.process_message("I'm feeling sad today")
    assert isinstance(response, dict)
    assert 'response' in response
    assert isinstance(response['response'], str)
    assert len(response['response']) > 0

    # Test question
    response = chatbot.process_message("What should I do?")
    assert isinstance(response, dict)
    assert 'response' in response
    assert isinstance(response['response'], str)
    assert len(response['response']) > 0

def test_context_awareness(chatbot):
    # Test conversation flow
    chatbot.process_message("I'm feeling anxious")
    response = chatbot.process_message("What should I do?")
    assert isinstance(response, dict)
    assert 'response' in response
    response_text = response['response'].lower()
    assert "anxiety" in response_text or "worry" in response_text or "afraid" in response_text or "fear" in response_text

def test_sentiment_analysis(chatbot):
    # Test positive sentiment
    response = chatbot.process_message("I'm so happy today!")
    assert isinstance(response, dict)
    assert 'response' in response
    response_text = response['response'].lower()
    assert "happy" in response_text or "joy" in response_text or "happiness" in response_text

    # Test negative sentiment
    response = chatbot.process_message("I'm really upset")
    assert isinstance(response, dict)
    assert 'response' in response
    response_text = response['response'].lower()
    assert "upset" in response_text or "difficult" in response_text or "down" in response_text or "sad" in response_text
