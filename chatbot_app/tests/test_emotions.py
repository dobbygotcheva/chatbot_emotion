#!/usr/bin/env python3
"""
Test script for emotion detection in the chatbot.
This script tests the emotion detection capabilities of the EnhancedEmotionDetector.
"""

import sys
import os
import json

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot

def test_emotion_detection():
    chatbot = AdvancedChatbot()

    # Test messages for each emotion
    test_cases = {
        'achievement': [
            "I took all my exams and passed!",
            "I found myself a new job!",
            "I have put off weight!",
            "I finally completed my degree!",
            "I reached my fitness goal today!"
        ],
        'joy': [
            "I am so happy today! 😊",
            "This is wonderful news!",
            "I feel great about this decision",
            "I'm overjoyed with the results",
            "This makes me so delighted"
        ],
        'sadness': [
            "I am feeling sad today",
            "This is so depressing",
            "I miss you so much",
            "This breaks my heart",
            "I wish things were different"
        ],
        'anger': [
            "I am furious about this situation",
            "This is completely unacceptable",
            "I hate when this happens",
            "I'm so angry right now",
            "This makes me really mad"
        ],
        'fear': [
            "I'm scared of what might happen",
            "This is really frightening",
            "I'm worried about the future",
            "I don't feel safe",
            "This terrifies me"
        ],
        'surprise': [
            "I'm so surprised by this!",
            "Wow, I didn't see that coming",
            "This is amazing!",
            "I'm shocked by this news",
            "Oh my god, really?"
        ],
        'trust': [
            "I trust your judgment completely",
            "You've always been reliable",
            "I have faith in your abilities",
            "I know you can do this",
            "I feel confident about this"
        ],
        'grief': [
            "I'm grieving the loss of my beloved pet",
            "The pain of losing my mother is overwhelming",
            "I miss them so much",
            "This loss has left me broken",
            "I'm still mourning their passing"
        ],
        'relief': [
            "I'm so relieved this is over",
            "What a weight off my shoulders",
            "I can finally breathe again",
            "The stress is gone now",
            "I feel much better now"
        ],
        'dread': [
            "I'm dreading tomorrow's presentation",
            "The thought of this fills me with dread",
            "I don't want to face this",
            "I'm filled with dread about the future",
            "This is dreadful news"
        ],
        'panic': [
            "I'm panicking right now",
            "This is a complete disaster",
            "I need to do something now",
            "I'm losing control",
            "This is too overwhelming"
        ],
        'disgust': [
            "This is absolutely revolting",
            "I'm disgusted by this behavior",
            "This makes me feel sick",
            "I can't stand this",
            "This is repulsive"
        ],
        'appalled': [
            "I'm appalled by their actions",
            "This is completely unacceptable",
            "I can't believe this happened",
            "This is outrageous",
            "I'm deeply disturbed by this"
        ],
        'desperation': [
            "I feel so worthless and useless",
            "I want to give up on everything",
            "I feel fat and ugly and no one loves me",
            "What's the point of living anymore",
            "I hate myself and my life is pointless"
        ]
    }

    print("\nTesting Emotion Detection System")
    print("=" * 50)

    for emotion, messages in test_cases.items():
        print(f"\nTesting {emotion.upper()} detection:")
        print("-" * 30)
        for message in messages:
            result = chatbot.analyze_emotion(message)
            print(f"\nMessage: {message}")
            print(f"Detected emotion: {result['emotion']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print("Top 3 emotions:")
            sorted_scores = sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)[:3]
            for emotion, score in sorted_scores:
                print(f"  {emotion}: {score:.2f}")

if __name__ == "__main__":
    test_emotion_detection() 
