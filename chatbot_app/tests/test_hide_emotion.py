"""
Test script to verify that the hide_emotion flag is correctly set when the chatbot transitions to drink recommendation mode.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot

class TestHideEmotion(unittest.TestCase):
    """Test cases for the hide_emotion flag in drink recommendation responses."""

    def setUp(self):
        """Set up the test environment."""
        self.chatbot = AdvancedChatbot()

    def test_hide_emotion_flag_in_drink_recommendation(self):
        """Test that the hide_emotion flag is set to True when the chatbot transitions to drink recommendation mode."""
        # First, get a regular response (not drink recommendation)
        regular_response = self.chatbot.process_message("I am feeling happy today")
        
        # Verify that hide_emotion is False or not set for regular responses
        self.assertFalse(
            regular_response.get('hide_emotion', False),
            "hide_emotion flag should be False or not set for regular responses"
        )
        
        # Now, trigger a drink recommendation
        drink_response = self.chatbot.process_message("Can you recommend a drink for me?")
        
        # Verify that hide_emotion is True for drink recommendation responses
        self.assertTrue(
            drink_response.get('hide_emotion', False),
            "hide_emotion flag should be True for drink recommendation responses"
        )
        
        # Continue the drink recommendation flow
        # Get the current question
        current_question = self.chatbot.context['current_drink_question']
        self.assertIsNotNone(current_question)
        
        # Find a valid answer for the question
        valid_answer = None
        for question in self.chatbot.drink_recommender.personality_questions:
            if question['question'] == current_question:
                valid_answer = question['options'][0]['text']
                break
        
        self.assertIsNotNone(valid_answer, "Could not find a valid answer for the question")
        
        # Answer the question
        follow_up_response = self.chatbot.process_message(valid_answer)
        
        # Verify that hide_emotion is still True for follow-up responses in the drink recommendation flow
        self.assertTrue(
            follow_up_response.get('hide_emotion', False),
            "hide_emotion flag should be True for follow-up responses in the drink recommendation flow"
        )

if __name__ == '__main__':
    unittest.main()