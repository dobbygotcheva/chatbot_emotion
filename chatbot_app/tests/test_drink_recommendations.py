"""
Test script for the drink recommendation feature of the chatbot.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot
from chatbot_app.chatbot.drinks_recommendations import DrinkRecommender

class TestDrinkRecommendations(unittest.TestCase):
    """Test cases for the drink recommendation feature."""

    def setUp(self):
        """Set up the test environment."""
        self.chatbot = AdvancedChatbot()

    def test_drink_recommendation_detection(self):
        """Test that the chatbot can detect drink recommendation requests."""
        # Test various drink recommendation requests
        requests = [
            "Can you recommend a drink for me?",
            "What drink should I have tonight?",
            "I need a cocktail recommendation",
            "Help me choose a beer",
            "What wine would go well with my mood?"
        ]

        for request in requests:
            self.assertTrue(
                self.chatbot.is_drink_recommendation_request(request),
                f"Failed to detect drink recommendation request: {request}"
            )

        # Test non-drink recommendation messages
        non_requests = [
            "How are you today?",
            "Tell me a joke",
            "What's the weather like?",
            "I'm feeling sad"
        ]

        for message in non_requests:
            self.assertFalse(
                self.chatbot.is_drink_recommendation_request(message),
                f"Incorrectly detected as drink recommendation request: {message}"
            )

    def test_drink_recommendation_flow(self):
        """Test the complete drink recommendation flow."""
        # Start the recommendation flow
        response = self.chatbot.process_message("Can you recommend a drink for me?")

        # Verify that the chatbot asks a question (look for a question mark or specific question phrases)
        self.assertTrue(
            "?" in response['response'] or 
            any(phrase in response['response'].lower() for phrase in [
                "how do you", "what kind of", "how would", "tell me about"
            ]),
            f"Response does not contain a question: {response['response']}"
        )
        self.assertEqual(self.chatbot.context['drink_recommendation_state'], 'asking_questions')

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

        # Answer the first question
        response = self.chatbot.process_message(valid_answer)

        # Verify that the chatbot either asks another question or gives a recommendation
        if self.chatbot.context['drink_recommendation_state'] == 'asking_questions':
            # It asked another question
            self.assertTrue(
                "?" in response['response'] or 
                any(phrase in response['response'].lower() for phrase in [
                    "how do you", "what kind of", "how would", "tell me about"
                ]),
                f"Response does not contain a question: {response['response']}"
            )

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

            # Answer the second question
            response = self.chatbot.process_message(valid_answer)

        # Now it should give a recommendation
        self.assertIn("enjoy", response['response'].lower())
        self.assertIsNone(self.chatbot.context['drink_recommendation_state'])

    def test_drink_recommender_direct(self):
        """Test the DrinkRecommender class directly."""
        recommender = DrinkRecommender()

        # Test setting emotion
        recommender.set_emotion("joy")
        self.assertEqual(recommender.user_profile['emotion'], "joy")

        # Test getting a question
        question = recommender.get_next_question()
        self.assertIsNotNone(question)
        self.assertIn('question', question)
        self.assertIn('options', question)

        # Test processing an answer
        valid_answer = question['options'][0]['text']
        result = recommender.process_answer(question['question'], valid_answer)
        self.assertTrue(result)

        # Test getting a recommendation
        recommendation = recommender.get_drink_recommendation()
        self.assertIn('drink', recommendation)
        self.assertIn('explanation', recommendation)

        # Test the recommendation message
        message = recommender.get_recommendation_message()
        # Check that the message contains the drink name and at least one of the common closing elements
        self.assertTrue(
            any(phrase in message['response'] for phrase in ["Enjoy", "Cheers", "Savor", "waiting for you", "great experience"]),
            f"Message doesn't contain any expected closing phrases: {message}"
        )

if __name__ == '__main__':
    unittest.main()
