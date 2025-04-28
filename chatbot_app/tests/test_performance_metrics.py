#!/usr/bin/env python3
"""
Performance Metrics Testing Module

This module evaluates the performance of the emotion detection system using:
- Accuracy metrics (precision, recall, F1-score)
- Latency measurements
- Memory usage profiling
- Mixed-emotion detection accuracy
- Emotion class coverage

Results are formatted for presentation.
"""

import os
import sys
import time
import json
import numpy as np
from memory_profiler import memory_usage
from collections import defaultdict, Counter
from sklearn.metrics import precision_score, recall_score, f1_score

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from chatbot_app.chatbot.advanced_chatbot import AdvancedChatbot

class PerformanceMetricsTester:
    """Tests and reports on chatbot performance metrics."""

    def __init__(self):
        """Initialize the tester with a chatbot instance and test datasets."""
        self.chatbot = AdvancedChatbot()

        # Ground truth datasets for emotion detection
        self.accuracy_dataset = [
            # Format: (message, primary_emotion, possible_secondary_emotions)
            ("I'm so happy today!", "joy", ["optimism"]),
            ("That makes me really angry.", "anger", []),
            ("I'm feeling sad about what happened.", "sadness", ["grief"]),
            ("I'm worried about the upcoming exam.", "fear", ["panic"]),
            ("That's disgusting!", "disgust", []),
            ("Wow, I didn't expect that!", "surprise", ["realisation"]),
            ("I love this so much!", "love", ["joy"]),
            ("I trust you to handle this.", "trust", []),
            ("I miss my old friends.", "sadness", ["nostalgia"]),
            ("I can't take this anymore.", "desperation", ["sadness"]),
            ("I just found out I got the job!", "achievement", ["joy", "surprise"]),
            ("I feel empty inside.", "sadness", ["desperation"]),
            ("I'm relieved it's finally over.", "relief", []),
            ("I'm so stressed I can't breathe.", "panic", ["fear"]),
            ("I believe in you completely.", "trust", ["love"]),
            ("My heart is broken after the loss.", "grief", ["sadness"]),
        ]

        # Mixed emotion test cases
        self.mixed_emotion_dataset = [
            # Format: (message, [expected_emotions])
            ("I'm excited but nervous about the presentation.", ["joy", "fear"]),
            ("I'm happy for him but also a bit jealous.", ["joy", "anger"]),
            ("I'm sad it's over but grateful for the experience.", ["sadness", "trust"]),
            ("I'm relieved but disappointed at the same time.", ["relief", "sadness"]),
            ("I'm scared but also curious to try.", ["fear", "curiosity"]),
            ("I love it but I'm worried about the cost.", ["love", "fear"]),
            ("I'm proud of my work but anxious about the feedback.", ["achievement", "fear"]),
            ("I'm angry about what happened but trying to stay positive.", ["anger", "optimism"]),
            ("I trust the process but fear the outcome.", ["trust", "fear"]),
            ("I'm surprised and a bit uncomfortable with the change.", ["surprise", "fear"]),
        ]

        # Dataset for testing latency with various message lengths
        self.latency_dataset = [
            "Hi.",  # Very short
            "I feel good today.",  # Short
            "I'm having mixed feelings about the upcoming meeting with the new team members.",  # Medium
            "I've been thinking a lot about what happened yesterday at the conference, and I'm not sure how to process all the emotions I'm experiencing right now.",  # Long
            "After carefully considering all the factors involved in the situation that occurred during our last interaction, I've come to realize that my emotional response was quite complex, involving elements of surprise, disappointment, and perhaps a touch of relief that things didn't escalate further than they did."  # Very long
        ]

        # Track all emotions that should be detectable
        self.all_emotions = set(self.chatbot.emotion_patterns.keys())

        # Results storage
        self.results = {
            "accuracy": {},
            "latency": {},
            "memory_usage": {},
            "mixed_emotion_detection": {},
            "emotion_coverage": {},
            "summary": {}
        }

    def test_accuracy(self):
        """Test the accuracy of emotion detection against ground truth data."""
        print("\nTesting Accuracy Metrics...")

        # Lists to store ground truth and predictions
        y_true = []
        y_pred = []
        confidence_scores = []

        # Process each test case
        for message, primary_emotion, _ in self.accuracy_dataset:
            start_time = time.time()
            result = self.chatbot.analyze_emotion(message)

            # Add to ground truth and predictions
            y_true.append(primary_emotion)
            y_pred.append(result['emotion'])
            confidence_scores.append(result['confidence'])

            print(f"Message: \"{message}\"")
            print(f"Expected: {primary_emotion}, Predicted: {result['emotion']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print("-" * 50)

        # Calculate metrics
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        # Calculate accuracy (direct matches)
        accuracy = sum(1 for true, pred in zip(y_true, y_pred) if true == pred) / len(y_true)

        # Store results
        self.results["accuracy"] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "direct_accuracy": accuracy,
            "average_confidence": np.mean(confidence_scores),
            "test_cases": len(y_true)
        }

        print(f"\nAccuracy Results:")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print(f"Direct Accuracy: {accuracy:.4f}")
        print(f"Average Confidence: {np.mean(confidence_scores):.4f}")

    def test_latency(self):
        """Test the processing latency for messages of different lengths."""
        print("\nTesting Latency...")

        latency_by_length = defaultdict(list)
        all_latencies = []

        # Run multiple iterations for more reliable measurements
        iterations = 5

        for message in self.latency_dataset:
            # Classify message length
            if len(message) < 10:
                length_category = "very_short"
            elif len(message) < 30:
                length_category = "short"
            elif len(message) < 100:
                length_category = "medium"
            elif len(message) < 200:
                length_category = "long"
            else:
                length_category = "very_long"

            latencies = []
            # Multiple runs to get average performance
            for _ in range(iterations):
                start_time = time.time()
                _ = self.chatbot.analyze_emotion(message)
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                latencies.append(latency)

            # Use median to avoid outliers
            median_latency = np.median(latencies)
            latency_by_length[length_category].append(median_latency)
            all_latencies.extend(latencies)

            print(f"Message length: {len(message)} chars ({length_category})")
            print(f"Median Latency: {median_latency:.2f} ms")
            print(f"Message: \"{message[:50]}{'...' if len(message) > 50 else ''}\"")
            print("-" * 50)

        # Calculate statistics
        latency_stats = {}
        for length, values in latency_by_length.items():
            latency_stats[length] = {
                "min": min(values),
                "max": max(values),
                "avg": np.mean(values),
                "median": np.median(values)
            }

        # Overall statistics
        overall_stats = {
            "min": min(all_latencies),
            "max": max(all_latencies),
            "avg": np.mean(all_latencies),
            "median": np.median(all_latencies),
            "p95": np.percentile(all_latencies, 95)  # 95th percentile
        }

        # Store results
        self.results["latency"] = {
            "by_length": latency_stats,
            "overall": overall_stats
        }

        print(f"\nLatency Results:")
        print(f"Overall Average: {overall_stats['avg']:.2f} ms")
        print(f"Overall Median: {overall_stats['median']:.2f} ms")
        print(f"95th Percentile: {overall_stats['p95']:.2f} ms")

    def test_memory_usage(self):
        """Test memory usage during emotion detection."""
        print("\nTesting Memory Usage...")

        def analyze_batch():
            """Function to analyze a batch of messages for memory profiling."""
            results = []
            for message in self.accuracy_dataset:
                results.append(self.chatbot.analyze_emotion(message[0]))
            return results

        # Measure memory usage
        memory_usage_data = memory_usage(
            (analyze_batch, [], {}),
            interval=0.1,
            timeout=10
        )

        # Calculate statistics
        baseline = memory_usage_data[0]  # Initial memory usage
        peak = max(memory_usage_data)
        avg = np.mean(memory_usage_data)

        # Store results
        self.results["memory_usage"] = {
            "baseline_mb": baseline,
            "peak_mb": peak,
            "average_mb": avg,
            "increase_mb": peak - baseline
        }

        print(f"Baseline Memory: {baseline:.2f} MB")
        print(f"Peak Memory: {peak:.2f} MB")
        print(f"Average Memory: {avg:.2f} MB")
        print(f"Memory Increase: {peak - baseline:.2f} MB")

    def test_mixed_emotion_detection(self):
        """Test the accuracy of detecting mixed emotions."""
        print("\nTesting Mixed Emotion Detection...")

        correct_detections = 0
        partial_detections = 0
        total_cases = len(self.mixed_emotion_dataset)
        coverage_scores = []

        for message, expected_emotions in self.mixed_emotion_dataset:
            result = self.chatbot.analyze_emotion(message)

            # Get the top 2 predicted emotions
            top_emotions = sorted(
                result['scores'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
            predicted_emotions = [emotion for emotion, _ in top_emotions]

            # Check how many expected emotions were correctly identified
            matches = sum(1 for emotion in expected_emotions if emotion in predicted_emotions)
            coverage = matches / len(expected_emotions)
            coverage_scores.append(coverage)

            if matches == len(expected_emotions):
                correct_detections += 1
            elif matches > 0:
                partial_detections += 1

            print(f"Message: \"{message}\"")
            print(f"Expected emotions: {expected_emotions}")
            print(f"Predicted top emotions: {predicted_emotions}")
            print(f"Coverage: {coverage:.2f}")
            print("-" * 50)

        # Calculate metrics
        full_accuracy = correct_detections / total_cases
        partial_accuracy = partial_detections / total_cases
        average_coverage = np.mean(coverage_scores)

        # Store results
        self.results["mixed_emotion_detection"] = {
            "full_matches": full_accuracy,
            "partial_matches": partial_accuracy,
            "average_coverage": average_coverage,
            "test_cases": total_cases
        }

        print(f"\nMixed Emotion Detection Results:")
        print(f"Full Matches: {full_accuracy:.4f}")
        print(f"Partial Matches: {partial_accuracy:.4f}")
        print(f"Average Coverage: {average_coverage:.4f}")

    def test_emotion_coverage(self):
        """Test coverage of all emotion classes."""
        print("\nTesting Emotion Class Coverage...")

        # Collect all detected emotions across test cases
        detected_emotions = set()
        emotion_counts = Counter()

        # Process all messages from both datasets
        all_messages = [msg for msg, _, _ in self.accuracy_dataset] + \
                      [msg for msg, _ in self.mixed_emotion_dataset]

        for message in all_messages:
            result = self.chatbot.analyze_emotion(message)

            # Add all emotions with non-zero scores
            for emotion, score in result['scores'].items():
                if score > 0:
                    detected_emotions.add(emotion)
                    emotion_counts[emotion] += 1

        # Calculate coverage
        total_emotions = len(self.all_emotions)
        detected_count = len(detected_emotions)
        coverage_rate = detected_count / total_emotions if total_emotions > 0 else 0

        # Missing emotions
        missing_emotions = self.all_emotions - detected_emotions

        # Store results
        self.results["emotion_coverage"] = {
            "total_emotions": total_emotions,
            "detected_emotions": detected_count,
            "coverage_rate": coverage_rate,
            "missing_emotions": list(missing_emotions),
            "emotion_frequency": dict(emotion_counts)
        }

        print(f"Total emotion classes: {total_emotions}")
        print(f"Detected emotion classes: {detected_count}")
        print(f"Coverage rate: {coverage_rate:.4f}")

        if missing_emotions:
            print(f"Missing emotions: {missing_emotions}")

        # Print most frequent emotions
        print("\nTop 5 most detected emotions:")
        for emotion, count in emotion_counts.most_common(5):
            print(f"{emotion}: {count} occurrences")

    def generate_summary(self):
        """Generate a summary of all performance metrics."""
        # Ensure all tests have been run
        if not all(key in self.results for key in ["accuracy", "latency", "memory_usage", 
                                                  "mixed_emotion_detection", "emotion_coverage"]):
            print("Warning: Not all tests have been run before generating summary.")

        summary = {
            "accuracy": {
                "precision": self.results.get("accuracy", {}).get("precision", 0),
                "recall": self.results.get("accuracy", {}).get("recall", 0),
                "f1_score": self.results.get("accuracy", {}).get("f1_score", 0),
            },
            "latency": {
                "median_ms": self.results.get("latency", {}).get("overall", {}).get("median", 0),
                "p95_ms": self.results.get("latency", {}).get("overall", {}).get("p95", 0),
            },
            "memory": {
                "peak_mb": self.results.get("memory_usage", {}).get("peak_mb", 0),
                "increase_mb": self.results.get("memory_usage", {}).get("increase_mb", 0),
            },
            "mixed_emotions": {
                "accuracy": self.results.get("mixed_emotion_detection", {}).get("full_matches", 0),
                "partial_accuracy": self.results.get("mixed_emotion_detection", {}).get("partial_matches", 0),
            },
            "emotion_coverage": {
                "rate": self.results.get("emotion_coverage", {}).get("coverage_rate", 0),
                "missing_count": len(self.results.get("emotion_coverage", {}).get("missing_emotions", [])),
            },
            "benchmarks": {
                "accuracy_target": 0.7,  # 70% accuracy benchmark
                "latency_target_ms": 500,  # 500ms latency benchmark
                "memory_target_mb": 200,  # 200MB memory usage benchmark
                "coverage_target": 0.73,  # 73% emotion coverage benchmark
            }
        }

        # Add pass/fail indicators for benchmarks
        summary["benchmarks"]["accuracy_passed"] = summary["accuracy"]["f1_score"] >= summary["benchmarks"]["accuracy_target"]
        summary["benchmarks"]["latency_passed"] = summary["latency"]["p95_ms"] <= summary["benchmarks"]["latency_target_ms"]
        summary["benchmarks"]["memory_passed"] = summary["memory"]["peak_mb"] <= summary["benchmarks"]["memory_target_mb"]
        summary["benchmarks"]["coverage_passed"] = summary["emotion_coverage"]["rate"] >= summary["benchmarks"]["coverage_target"]

        # Store summary
        self.results["summary"] = summary

        return summary

    def run_all_tests(self):
        """Run all performance tests and generate a summary."""
        print("Starting Performance Metrics Testing...")
        print("=" * 70)

        # Run all tests
        self.test_accuracy()
        self.test_latency()
        self.test_memory_usage()
        self.test_mixed_emotion_detection()
        self.test_emotion_coverage()

        # Generate summary
        summary = self.generate_summary()

        print("\n" + "=" * 35)
        print("PERFORMANCE TESTING SUMMARY")
        print("=" * 35)

        print(f"\nAccuracy Metrics:")
        print(f"  Precision: {summary['accuracy']['precision']:.4f}")
        print(f"  Recall: {summary['accuracy']['recall']:.4f}")
        print(f"  F1-Score: {summary['accuracy']['f1_score']:.4f}")
        print(f"  Benchmark ({summary['benchmarks']['accuracy_target']:.2f}): {'PASSED' if summary['benchmarks']['accuracy_passed'] else 'FAILED'}")

        print(f"\nLatency Metrics:")
        print(f"  Median: {summary['latency']['median_ms']:.2f} ms")
        print(f"  95th Percentile: {summary['latency']['p95_ms']:.2f} ms")
        print(f"  Benchmark ({summary['benchmarks']['latency_target_ms']} ms): {'PASSED' if summary['benchmarks']['latency_passed'] else 'FAILED'}")

        print(f"\nMemory Usage:")
        print(f"  Peak: {summary['memory']['peak_mb']:.2f} MB")
        print(f"  Increase: {summary['memory']['increase_mb']:.2f} MB")
        print(f"  Benchmark ({summary['benchmarks']['memory_target_mb']} MB): {'PASSED' if summary['benchmarks']['memory_passed'] else 'FAILED'}")

        print(f"\nMixed Emotion Detection:")
        print(f"  Full Match Rate: {summary['mixed_emotions']['accuracy']:.4f}")
        print(f"  Partial Match Rate: {summary['mixed_emotions']['partial_accuracy']:.4f}")

        print(f"\nEmotion Class Coverage:")
        print(f"  Coverage Rate: {summary['emotion_coverage']['rate']:.4f}")
        print(f"  Missing Emotions: {summary['emotion_coverage']['missing_count']}")
        print(f"  Benchmark ({summary['benchmarks']['coverage_target']:.2f}): {'PASSED' if summary['benchmarks']['coverage_passed'] else 'FAILED'}")

        return self.results

    def export_results(self, filename='chatbot_performance_metrics.json'):
        """Export results to a JSON file for further analysis or presentation."""
        # Create a deep copy of the results to avoid modifying the original
        import copy
        results_copy = copy.deepcopy(self.results)

        # Helper function to ensure all values in a dictionary are JSON serializable
        def ensure_serializable(obj):
            if isinstance(obj, dict):
                return {k: ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_serializable(item) for item in obj]
            elif isinstance(obj, (bool, int, float, str, type(None))):
                return obj
            else:
                # Convert any other type to string
                return str(obj)

        # Ensure all values in the results are JSON serializable
        serializable_results = ensure_serializable(results_copy)

        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"\nResults exported to {filename}")
        return filename


def run_performance_tests():
    """Run all performance tests and export results."""
    tester = PerformanceMetricsTester()
    results = tester.run_all_tests()
    json_file = tester.export_results()
    return results, json_file


if __name__ == "__main__":
    run_performance_tests()
