import unittest
import sys
import os
import math
import re
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path to import the chatbot module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot.advanced_chatbot import AdvancedChatbot

class TestEmotionRecognition(unittest.TestCase):
    """Tests for the emotion recognition functionality of the AdvancedChatbot."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Mock the logger to avoid actual logging
        with patch('logging.getLogger'):
            self.chatbot = AdvancedChatbot()
        
        # Set up a mock context
        self.chatbot.context = {'session_emotions': ['neutral', 'joy']}
        
    def test_basic_emotions(self):
        """Test recognition of basic emotions with explicit expressions."""
        test_cases = [
            ("I am happy today.", "joy"),
            ("I feel sad right now.", "sadness"),
            ("I'm angry about what happened.", "anger"),
            ("I'm afraid of the dark.", "fear"),
            ("Wow! That's surprising!", "surprise"),
            ("I trust you completely.", "trust"),
            ("I'm confused about these instructions.", "confusion"),
            ("I feel disgusted by that behavior.", "disgust"),
        ]
        
        for message, expected_emotion in test_cases:
            result = self.chatbot.analyze_emotion(message)
            self.assertEqual(result['emotion'], expected_emotion, 
                             f"Failed to detect {expected_emotion} in '{message}'. Got {result['emotion']} instead.")
            
            # Check that the sum of scores equals 1.0 (within rounding error)
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5, 
                                  msg=f"Sum of emotion scores is {total_score}, expected 1.0")
    
    def test_neutral_statements(self):
        """Test recognition of neutral statements."""
        test_cases = [
            "The sky is blue.",
            "Today is Tuesday.",
            "I need to buy groceries.",
            "The meeting starts at 3 PM.",
        ]
        
        for message in test_cases:
            result = self.chatbot.analyze_emotion(message)
            # Either neutral should be detected, or confidence should be low
            if result['emotion'] != 'neutral':
                self.assertLess(result['confidence'], 0.6, 
                                f"Non-neutral emotion {result['emotion']} detected with high confidence in neutral statement: '{message}'")
                
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_mixed_emotions(self):
        """Test recognition of mixed emotions."""
        test_cases = [
            ("I'm excited about the trip but nervous about flying.", ["excitement", "fear"]),
            ("I'm happy with my promotion but sad to leave my team.", ["joy", "sadness"]),
            ("I'm grateful for the opportunity but worried about failing.", ["achievement", "fear"]),
        ]
        
        for message, expected_emotions in test_cases:
            result = self.chatbot.analyze_emotion(message)
            
            # Either the primary or mixed emotion should match one of the expected emotions
            primary_matches = result['emotion'] in expected_emotions
            mixed_matches = result.get('mixed_emotion') in expected_emotions
            
            self.assertTrue(primary_matches or mixed_matches, 
                           f"Failed to detect any of {expected_emotions} in '{message}'. Got {result['emotion']} and {result.get('mixed_emotion')}")
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_negated_emotions(self):
        """Test recognition of negated emotions."""
        test_cases = [
            ("I'm not happy with the results.", ["disappointment", "sadness", "frustration", "anger"]),
            ("I don't feel angry anymore.", ["relief", "neutral"]),
            ("I'm not afraid of public speaking.", ["confidence", "neutral", "courage"]),
        ]
        
        for message, possible_emotions in test_cases:
            result = self.chatbot.analyze_emotion(message)
            
            # The emotion should not be the negated one
            if "not happy" in message.lower():
                self.assertNotEqual(result['emotion'], "joy", 
                                   f"Detected joy in '{message}' despite negation.")
            elif "don't feel angry" in message.lower():
                self.assertNotEqual(result['emotion'], "anger", 
                                   f"Detected anger in '{message}' despite negation.")
            elif "not afraid" in message.lower():
                self.assertNotEqual(result['emotion'], "fear", 
                                   f"Detected fear in '{message}' despite negation.")
                
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_implicit_emotions(self):
        """Test recognition of implicit emotions."""
        test_cases = [
            ("My dog passed away last week.", ["sadness", "grief"]),
            ("I didn't get the job I applied for.", ["disappointment", "sadness"]),
            ("They just announced budget cuts at work.", ["worry", "fear", "concern"]),
            ("My flight got delayed by 5 hours.", ["frustration", "anger", "disappointment"]),
        ]
        
        for message, possible_emotions in test_cases:
            result = self.chatbot.analyze_emotion(message)
            found_match = result['emotion'] in possible_emotions or result.get('mixed_emotion') in possible_emotions
            
            self.assertTrue(found_match, 
                           f"Failed to detect any of {possible_emotions} in '{message}'. Got {result['emotion']} and {result.get('mixed_emotion')}")
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_single_words(self):
        """Test recognition of single emotion words."""
        test_cases = [
            ("Happy.", "joy"),
            ("Sad.", "sadness"),
            ("Angry.", "anger"),
            ("Afraid.", "fear"),
        ]
        
        for message, expected_emotion in test_cases:
            result = self.chatbot.analyze_emotion(message)
            self.assertEqual(result['emotion'], expected_emotion, 
                             f"Failed to detect {expected_emotion} in '{message}'. Got {result['emotion']} instead.")
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_emotion_intensity(self):
        """Test recognition of emotion intensity."""
        low_intensity = self.chatbot.analyze_emotion("I'm a bit annoyed.")
        medium_intensity = self.chatbot.analyze_emotion("I'm very annoyed.")
        high_intensity = self.chatbot.analyze_emotion("I'm extremely annoyed.")
        extreme_intensity = self.chatbot.analyze_emotion("I'm absolutely furious.")
        
        # Check that intensities increase as expected
        self.assertLessEqual(low_intensity['confidence'], medium_intensity['confidence'])
        self.assertLessEqual(medium_intensity['confidence'], high_intensity['confidence'])
        self.assertLessEqual(high_intensity['confidence'], extreme_intensity['confidence'])
        
        # Check that the sum of scores equals 1.0
        for result in [low_intensity, medium_intensity, high_intensity, extreme_intensity]:
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_pattern_specific(self):
        """Test recognition of specific emotional patterns."""
        test_cases = [
            ("I didn't know that could happen!", ["realisation", "surprise"]),
            ("I feel empty inside.", ["sadness", "desperation"]),
            ("I just found out about the news.", ["surprise", "realisation"]),
            ("That's revolting.", ["disgust"]),
        ]
        
        for message, possible_emotions in test_cases:
            result = self.chatbot.analyze_emotion(message)
            found_match = result['emotion'] in possible_emotions or result.get('mixed_emotion') in possible_emotions
            
            self.assertTrue(found_match, 
                           f"Failed to detect any of {possible_emotions} in '{message}'. Got {result['emotion']} and {result.get('mixed_emotion')}")
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_context_window(self):
        """Test context window intensity modifiers."""
        low_intensity = self.chatbot.analyze_emotion("The frustrating situation.")
        high_intensity = self.chatbot.analyze_emotion("The extremely frustrating situation.")
        
        # The emotion should be the same, but intensity should be higher with modifier
        self.assertEqual(low_intensity['emotion'], high_intensity['emotion'])
        self.assertLessEqual(low_intensity['confidence'], high_intensity['confidence'])
        
        # Check that the sum of scores equals 1.0
        for result in [low_intensity, high_intensity]:
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_real_life_examples(self):
        """Test with real-life, complex examples from README."""
        test_cases = [
            "I was excited about the trip, but now I'm worried about the cost.",
            "I just got back from the interview. They said they'll let me know next week.",
            "I guess we could try that approach. It might work.",
            "I'm not upset, just a bit tired from all the work.",
            "The presentation went well, but I'm not sure if they understood all the key points.",
            "My car broke down on the way to the important meeting. Had to call a taxi.",
        ]
        
        for message in test_cases:
            result = self.chatbot.analyze_emotion(message)
            
            # We're testing that analysis completes without errors and scores sum to 1.0
            self.assertIsNotNone(result['emotion'])
            self.assertIsNotNone(result['confidence'])
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5, 
                                  msg=f"Sum of emotion scores for '{message}' is {total_score}, expected 1.0")
    
    def test_multiple_emotions(self):
        """Test with multiple emotions mentioned together."""
        result = self.chatbot.analyze_emotion("I am happy. I am sad. I am angry. I am afraid. I am surprised.")
        
        # Check that the model detects at least one of the emotions and possibly a mixed emotion
        possible_emotions = ["joy", "sadness", "anger", "fear", "surprise"]
        primary_match = result['emotion'] in possible_emotions
        mixed_match = result.get('mixed_emotion') in possible_emotions
        
        self.assertTrue(primary_match or mixed_match, 
                       f"Failed to detect any basic emotion. Got {result['emotion']} and {result.get('mixed_emotion')}")
        
        # Check that the sum of scores equals 1.0
        total_score = sum(result['scores'].values())
        self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_repeated_emotion(self):
        """Test with a single emotion repeated many times."""
        result = self.chatbot.analyze_emotion("Happy happy happy happy happy happy happy.")
        
        # Should detect joy with high confidence
        self.assertEqual(result['emotion'], "joy")
        self.assertGreater(result['confidence'], 0.7)
        
        # Check that the sum of scores equals 1.0
        total_score = sum(result['scores'].values())
        self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_suicidal_content(self):
        """Test detection of suicidal content which should trigger desperation."""
        test_cases = [
            "I want to end my life.",
            "I don't see any reason to live anymore.",
            "I can't take it anymore, I just want to die.",
        ]
        
        for message in test_cases:
            result = self.chatbot.analyze_emotion(message)
            self.assertEqual(result['emotion'], "desperation", 
                             f"Failed to detect desperation in suicidal content: '{message}'. Got {result['emotion']} instead.")
            
            # Should have high confidence for suicidal content
            self.assertGreater(result['confidence'], 0.7)
            
            # Check that the sum of scores equals 1.0
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5)
    
    def test_score_normalization(self):
        """Test that all emotion scores are properly normalized to sum to 1.0."""
        test_messages = [
            "I am happy today.",
            "I feel sad right now.",
            "I'm angry about what happened.",
            "I'm afraid of the dark.",
            "Wow! That's surprising!",
            "I trust you completely.",
            "I'm confused about these instructions.",
            "I feel disgusted by that behavior.",
            "I was excited about the trip but nervous about flying.",
            "I'm not happy with the results.",
            "My dog passed away last week.",
            "Happy.",
            "I'm a bit annoyed.",
            "I'm absolutely furious.",
            "I didn't know that could happen!",
            "I just found out about the news.",
            "I am happy. I am sad. I am angry. I am afraid. I am surprised.",
            "Happy happy happy happy happy happy happy.",
            "I want to end my life.",
        ]
        
        for message in test_messages:
            result = self.chatbot.analyze_emotion(message)
            total_score = sum(result['scores'].values())
            self.assertAlmostEqual(total_score, 1.0, places=5, 
                                  msg=f"Sum of emotion scores for '{message}' is {total_score}, expected 1.0")

if __name__ == '__main__':
    unittest.main()
