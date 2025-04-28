"""
Module for detecting implicit emotions in text messages.
"""

import re
from typing import Dict, List, Set

def detect_implicit_emotions(emotion_patterns: Dict, message: str) -> Dict[str, float]:
    """
    Detect implicit emotional content in a message that might not contain explicit emotion words.

    Args:
        emotion_patterns: Dictionary of emotion patterns
        message: The user's message

    Returns:
        Dict containing detected implicit emotions and their scores
    """
    implicit_emotions = {emotion: 0.0 for emotion in emotion_patterns.keys()}
    message_lower = message.lower()

    # Check for specific contexts mentioned in the issue
    # Realization and surprise in statements like "I didn't know cats could fly!"
    if re.search(r'\bi (didn\'t|did not) know\b', message_lower) or re.search(r'\bjust (found out|realized|discovered)\b', message_lower):
        implicit_emotions['realisation'] = implicit_emotions.get('realisation', 0.0) + 0.2  # Reduced from 0.4
        implicit_emotions['surprise'] = implicit_emotions.get('surprise', 0.0) + 0.15  # Reduced from 0.3

    # Desperation in statements like "I want to die"
    # Give a higher score to ensure consistent detection regardless of conversation history
    if re.search(r'\bi (want|wish|need) to (die|end it all|disappear|vanish|not exist)\b', message_lower) or re.search(r'\bi (can\'t|cannot) (take|handle|bear|stand|deal with) (it|this|life|living|anything) (anymore|any longer|another day)\b', message_lower):
        implicit_emotions['desperation'] = implicit_emotions.get('desperation', 0.0) + 0.8  # Reduced from 2.0
        implicit_emotions['sadness'] = implicit_emotions.get('sadness', 0.0) + 0.3  # Reduced from 0.5

    # Additional desperation indicators
    if re.search(r'\b(no (point|use|hope|future|reason to live|way out))\b', message_lower) or re.search(r'\b(what\'s the point|why bother|why try|why live|why continue|why go on|what\'s the use)\b', message_lower):
        implicit_emotions['desperation'] = implicit_emotions.get('desperation', 0.0) + 0.6  # Reduced from 1.5
        implicit_emotions['sadness'] = implicit_emotions.get('sadness', 0.0) + 0.2  # Reduced from 0.4

    return implicit_emotions
