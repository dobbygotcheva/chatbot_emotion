#!/usr/bin/env python3
"""
Performance Metrics Visualization Module

This module generates visualizations for the chatbot performance metrics
results, producing charts and diagrams for presentation purposes.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


class PerformanceVisualizer:
    """Generates visualizations for chatbot performance test results."""

    def __init__(self, results_file=None, results_data=None):
        """
        Initialize with either a results file path or direct results data.

        Args:
            results_file: Path to JSON results file
            results_data: Dictionary containing results data
        """
        if results_file and os.path.exists(results_file):
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        elif results_data:
            self.results = results_data
        else:
            raise ValueError("Either results_file or results_data must be provided")

        # Create output directory for charts
        self.output_dir = "performance_charts"
        os.makedirs(self.output_dir, exist_ok=True)

    def visualize_accuracy(self):
        """Create visualization for accuracy metrics."""
        if "accuracy" not in self.results:
            print("No accuracy data available")
            return

        accuracy_data = self.results["accuracy"]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data for plotting
        metrics = ['Precision', 'Recall', 'F1-Score', 'Direct Accuracy']
        values = [
            accuracy_data.get('precision', 0),
            accuracy_data.get('recall', 0),
            accuracy_data.get('f1_score', 0),
            accuracy_data.get('direct_accuracy', 0)
        ]

        # Set color based on benchmark
        benchmark = self.results.get('summary', {}).get('benchmarks', {}).get('accuracy_target', 0.85)
        colors = ['green' if v >= benchmark else 'red' for v in values]

        # Create bar chart
        bars = ax.bar(metrics, values, color=colors, alpha=0.7)

        # Add benchmark line
        ax.axhline(y=benchmark, color='blue', linestyle='--', 
                 label=f'Benchmark ({benchmark:.2f})')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom')

        # Customize chart
        ax.set_ylim(0, 1.1)
        ax.set_title('Emotion Detection Accuracy Metrics', fontsize=16)
        ax.set_ylabel('Score (0-1)', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend()

        # Add context
        test_cases = accuracy_data.get('test_cases', 0)
        avg_confidence = accuracy_data.get('average_confidence', 0)
        plt.figtext(0.5, 0.01, 
                   f"Based on {test_cases} test cases | Average confidence: {avg_confidence:.3f}",
                   ha='center', fontsize=10)

        plt.tight_layout(rect=[0, 0.03, 1, 0.97])

        # Save the chart
        output_path = os.path.join(self.output_dir, "accuracy_metrics.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def visualize_latency(self):
        """Create visualization for latency metrics."""
        if "latency" not in self.results:
            print("No latency data available")
            return

        latency_data = self.results["latency"]
        by_length = latency_data.get("by_length", {})
        overall = latency_data.get("overall", {})

        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Latency by message length
        if by_length:
            # Prepare data
            categories = []
            medians = []
            mins = []
            maxes = []

            # Order categories by length
            length_order = {'very_short': 0, 'short': 1, 'medium': 2, 'long': 3, 'very_long': 4}
            for category, values in sorted(by_length.items(), key=lambda x: length_order.get(x[0], 99)):
                categories.append(category.replace('_', ' ').title())
                medians.append(values.get('median', 0))
                mins.append(values.get('min', 0))
                maxes.append(values.get('max', 0))

            # Plot median latencies
            bars = ax1.bar(categories, medians, alpha=0.7)

            # Add min/max as error bars
            error = [np.array(medians) - np.array(mins), np.array(maxes) - np.array(medians)]
            ax1.errorbar(categories, medians, yerr=error, fmt='none', capsize=5, color='black')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}', ha='center', va='bottom')

            # Customize chart
            ax1.set_title('Latency by Message Length', fontsize=14)
            ax1.set_ylabel('Latency (ms)', fontsize=12)
            ax1.set_xticklabels(categories, rotation=30, ha='right')
            ax1.grid(axis='y', linestyle='--', alpha=0.7)

        # Plot 2: Overall latency distribution
        if overall:
            # Prepare data
            metrics = ['Min', 'Avg', 'Median', 'P95', 'Max']
            values = [
                overall.get('min', 0),
                overall.get('avg', 0),
                overall.get('median', 0),
                overall.get('p95', 0),
                overall.get('max', 0)
            ]

            # Set color based on benchmark
            benchmark = self.results.get('summary', {}).get('benchmarks', {}).get('latency_target_ms', 500)
            colors = ['green' if v <= benchmark else 'red' for v in values]

            # Create bar chart
            bars = ax2.bar(metrics, values, color=colors, alpha=0.7)

            # Add benchmark line
            ax2.axhline(y=benchmark, color='blue', linestyle='--', 
                      label=f'Benchmark ({benchmark} ms)')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}', ha='center', va='bottom')

            # Customize chart
            ax2.set_title('Overall Latency Metrics', fontsize=14)
            ax2.set_ylabel('Latency (ms)', fontsize=12)
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            ax2.legend()

        plt.suptitle('Emotion Detection Processing Latency', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Save the chart
        output_path = os.path.join(self.output_dir, "latency_metrics.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def visualize_memory(self):
        """Create visualization for memory usage metrics."""
        if "memory_usage" not in self.results:
            print("No memory usage data available")
            return

        memory_data = self.results["memory_usage"]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data for plotting
        labels = ['Baseline', 'Average', 'Peak']
        values = [
            memory_data.get('baseline_mb', 0),
            memory_data.get('average_mb', 0),
            memory_data.get('peak_mb', 0)
        ]

        # Set color based on benchmark
        benchmark = self.results.get('summary', {}).get('benchmarks', {}).get('memory_target_mb', 100)
        colors = ['green' if v <= benchmark else 'red' for v in values]

        # Create bar chart
        bars = ax.bar(labels, values, color=colors, alpha=0.7)

        # Add benchmark line
        ax.axhline(y=benchmark, color='blue', linestyle='--', 
                 label=f'Benchmark ({benchmark} MB)')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}', ha='center', va='bottom')

        # Add memory increase annotation
        memory_increase = memory_data.get('increase_mb', 0)
        plt.annotate(f'Memory Increase: {memory_increase:.1f} MB',
                    xy=(2, values[0]),
                    xytext=(2, (values[0] + values[2])/2),
                    arrowprops=dict(arrowstyle='->'),
                    fontsize=12)

        # Customize chart
        ax.set_title('Memory Usage During Emotion Detection', fontsize=16)
        ax.set_ylabel('Memory (MB)', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend()

        plt.tight_layout()

        # Save the chart
        output_path = os.path.join(self.output_dir, "memory_usage.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def visualize_mixed_emotion(self):
        """Create visualization for mixed emotion detection accuracy."""
        if "mixed_emotion_detection" not in self.results:
            print("No mixed emotion detection data available")
            return

        mixed_data = self.results["mixed_emotion_detection"]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data for plotting
        categories = ['Full Matches', 'Partial Matches', 'No Matches']
        values = [
            mixed_data.get('full_matches', 0),
            mixed_data.get('partial_matches', 0),
            1 - mixed_data.get('full_matches', 0) - mixed_data.get('partial_matches', 0)
        ]

        # Colors for different match types
        colors = ['#2ecc71', '#f39c12', '#e74c3c']

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=categories,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=(0.1, 0, 0)
        )

        # Customize text
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_weight('bold')

        # Add title and legend
        ax.set_title('Mixed Emotion Detection Accuracy', fontsize=16)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

        # Add context
        test_cases = mixed_data.get('test_cases', 0)
        avg_coverage = mixed_data.get('average_coverage', 0)
        plt.figtext(0.5, 0.01, 
                   f"Based on {test_cases} mixed emotion test cases | Average emotion coverage: {avg_coverage:.3f}",
                   ha='center', fontsize=10)

        plt.tight_layout(rect=[0, 0.03, 1, 0.97])

        # Save the chart
        output_path = os.path.join(self.output_dir, "mixed_emotion_detection.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def visualize_emotion_coverage(self):
        """Create visualization for emotion class coverage."""
        if "emotion_coverage" not in self.results:
            print("No emotion coverage data available")
            return

        coverage_data = self.results["emotion_coverage"]

        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Coverage gauge
        coverage_rate = coverage_data.get('coverage_rate', 0)
        benchmark = self.results.get('summary', {}).get('benchmarks', {}).get('coverage_target', 0.95)

        # Create a half-circle for the gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Draw gauge background
        ax1.plot(x, y, 'black', linewidth=2)
        ax1.fill_between(x, 0, y, color='lightgray', alpha=0.5)

        # Add benchmark line
        benchmark_theta = np.pi * benchmark
        benchmark_x = r * np.cos(benchmark_theta)
        benchmark_y = r * np.sin(benchmark_theta)
        ax1.plot([0, benchmark_x], [0, benchmark_y], 'b--', linewidth=2, label=f'Benchmark ({benchmark:.2f})')

        # Add needle
        coverage_theta = np.pi * (1 - coverage_rate)
        needle_x = r * np.cos(coverage_theta)
        needle_y = r * np.sin(coverage_theta)
        ax1.plot([0, needle_x], [0, needle_y], 'red', linewidth=3)

        # Add coverage percentage text
        ax1.text(0, -0.2, f'{coverage_rate*100:.1f}%', ha='center', va='center', fontsize=24)

        # Set colors based on benchmark
        if coverage_rate >= benchmark:
            color = 'green'
            result = 'PASSED'
        else:
            color = 'red'
            result = 'FAILED'

        # Add pass/fail indicator
        ax1.text(0, -0.4, result, ha='center', va='center', fontsize=18, 
                color=color, weight='bold')

        # Customize plot
        ax1.set_aspect('equal')
        ax1.set_xlim(-1.2, 1.2)
        ax1.set_ylim(-0.5, 1.2)
        ax1.axis('off')
        ax1.set_title('Emotion Class Coverage', fontsize=16)
        ax1.legend(loc='upper left')

        # Data for pie chart
        detected = coverage_data.get('detected_emotions', 0)
        missing = coverage_data.get('missing_emotions', [])
        missing_count = len(missing)

        # Plot 2: Detected vs Missing pie chart
        sizes = [detected, missing_count]
        labels = [f'Detected ({detected})', f'Missing ({missing_count})']
        colors = ['#2ecc71', '#e74c3c']

        # Check if there are any missing emotions
        if missing_count > 0:
            # Create pie chart
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, explode=(0, 0.1))

            # List missing emotions
            missing_str = ', '.join(missing[:5])
            if len(missing) > 5:
                missing_str += f', and {len(missing)-5} more'

            plt.figtext(0.75, 0.01, 
                       f"Missing emotions: {missing_str}",
                       ha='center', fontsize=10, color='#e74c3c')
        else:
            # If no missing emotions, show 100% coverage
            ax2.pie([1], labels=['All Emotions Detected (100%)'], colors=['#2ecc71'], autopct='%1.1f%%')

        # Customize plot
        ax2.set_aspect('equal')
        ax2.set_title('Detected vs Missing Emotions', fontsize=16)

        plt.suptitle('Emotion Class Coverage Analysis', fontsize=18)
        plt.tight_layout(rect=[0, 0.03, 1, 0.90])

        # Save the chart
        output_path = os.path.join(self.output_dir, "emotion_coverage.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def visualize_summary(self):
        """Create a summary dashboard of all metrics."""
        if "summary" not in self.results:
            print("No summary data available")
            return

        summary = self.results["summary"]

        # Create figure with grid for metrics
        fig, axs = plt.subplots(2, 2, figsize=(15, 12))

        # Flatten axes for easier access
        axs = axs.flatten()

        # Plot 1: Accuracy metrics (top-left)
        accuracy = summary.get('accuracy', {})
        accuracy_metrics = ['Precision', 'Recall', 'F1-Score']
        accuracy_values = [
            accuracy.get('precision', 0),
            accuracy.get('recall', 0),
            accuracy.get('f1_score', 0)
        ]
        accuracy_benchmark = summary.get('benchmarks', {}).get('accuracy_target', 0.85)
        accuracy_colors = ['green' if v >= accuracy_benchmark else 'red' for v in accuracy_values]

        bars1 = axs[0].bar(accuracy_metrics, accuracy_values, color=accuracy_colors, alpha=0.7)
        axs[0].axhline(y=accuracy_benchmark, color='blue', linestyle='--', label=f'Benchmark ({accuracy_benchmark:.2f})')
        for bar in bars1:
            height = bar.get_height()
            axs[0].text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.3f}', ha='center', va='bottom')

        axs[0].set_ylim(0, 1.1)
        axs[0].set_title('Accuracy Metrics', fontsize=14)
        axs[0].set_ylabel('Score (0-1)', fontsize=12)
        axs[0].grid(axis='y', linestyle='--', alpha=0.7)
        axs[0].legend()

        # Plot 2: Latency metrics (top-right)
        latency = summary.get('latency', {})
        latency_metrics = ['Median', '95th Percentile']
        latency_values = [
            latency.get('median_ms', 0),
            latency.get('p95_ms', 0)
        ]
        latency_benchmark = summary.get('benchmarks', {}).get('latency_target_ms', 500)
        latency_colors = ['green' if v <= latency_benchmark else 'red' for v in latency_values]

        bars2 = axs[1].bar(latency_metrics, latency_values, color=latency_colors, alpha=0.7)
        axs[1].axhline(y=latency_benchmark, color='blue', linestyle='--', label=f'Benchmark ({latency_benchmark} ms)')
        for bar in bars2:
            height = bar.get_height()
            axs[1].text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}', ha='center', va='bottom')

        axs[1].set_title('Latency Metrics', fontsize=14)
        axs[1].set_ylabel('Latency (ms)', fontsize=12)
        axs[1].grid(axis='y', linestyle='--', alpha=0.7)
        axs[1].legend()

        # Plot 3: Memory usage (bottom-left)
        memory = summary.get('memory', {})
        memory_metrics = ['Peak Memory', 'Memory Increase']
        memory_values = [
            memory.get('peak_mb', 0),
            memory.get('increase_mb', 0)
        ]
        memory_benchmark = summary.get('benchmarks', {}).get('memory_target_mb', 100)
        memory_colors = ['green' if v <= memory_benchmark else 'red' for v in memory_values]

        bars3 = axs[2].bar(memory_metrics, memory_values, color=memory_colors, alpha=0.7)
        axs[2].axhline(y=memory_benchmark, color='blue', linestyle='--', label=f'Benchmark ({memory_benchmark} MB)')
        for bar in bars3:
            height = bar.get_height()
            axs[2].text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{height:.1f}', ha='center', va='bottom')

        axs[2].set_title('Memory Usage', fontsize=14)
        axs[2].set_ylabel('Memory (MB)', fontsize=12)
        axs[2].grid(axis='y', linestyle='--', alpha=0.7)
        axs[2].legend()

        # Plot 4: Coverage and mixed emotions (bottom-right)
        coverage = summary.get('emotion_coverage', {}).get('rate', 0)
        mixed_full = summary.get('mixed_emotions', {}).get('accuracy', 0)
        mixed_partial = summary.get('mixed_emotions', {}).get('partial_accuracy', 0)

        coverage_benchmark = summary.get('benchmarks', {}).get('coverage_target', 0.95)

        metrics4 = ['Emotion Coverage', 'Mixed Emotion\nDetection (Full)', 'Mixed Emotion\nDetection (Partial)']
        values4 = [coverage, mixed_full, mixed_partial]
        colors4 = ['green' if values4[0] >= coverage_benchmark else 'red', 'blue', 'orange']

        bars4 = axs[3].bar(metrics4, values4, color=colors4, alpha=0.7)
        axs[3].axhline(y=coverage_benchmark, color='green', linestyle='--', label=f'Coverage Benchmark ({coverage_benchmark:.2f})')
        for bar in bars4:
            height = bar.get_height()
            axs[3].text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.3f}', ha='center', va='bottom')

        axs[3].set_ylim(0, 1.1)
        axs[3].set_title('Coverage & Mixed Emotion Detection', fontsize=14)
        axs[3].set_ylabel('Rate (0-1)', fontsize=12)
        axs[3].grid(axis='y', linestyle='--', alpha=0.7)
        axs[3].legend()

        # Overall pass/fail summary
        benchmarks_passed = sum([
            1 if summary.get('benchmarks', {}).get('accuracy_passed', False) else 0,
            1 if summary.get('benchmarks', {}).get('latency_passed', False) else 0,
            1 if summary.get('benchmarks', {}).get('memory_passed', False) else 0,
            1 if summary.get('benchmarks', {}).get('coverage_passed', False) else 0
        ])

        overall_status = f"Performance Summary: {benchmarks_passed}/4 benchmarks passed"
        if benchmarks_passed == 4:
            status_color = 'green'
        elif benchmarks_passed >= 2:
            status_color = 'orange'
        else:
            status_color = 'red'

        plt.suptitle(f"Emotion Detection Chatbot Performance Dashboard\n{overall_status}", 
                     fontsize=18, color=status_color)

        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Save the chart
        output_path = os.path.join(self.output_dir, "performance_summary.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_all_visualizations(self):
        """Generate all visualizations and return paths to output files."""
        output_files = {}

        print("Generating performance visualizations...")

        output_files['accuracy'] = self.visualize_accuracy()
        output_files['latency'] = self.visualize_latency()
        output_files['memory'] = self.visualize_memory()
        output_files['mixed_emotion'] = self.visualize_mixed_emotion()
        output_files['emotion_coverage'] = self.visualize_emotion_coverage()
        output_files['summary'] = self.visualize_summary()

        print(f"Visualizations saved to {self.output_dir}/")

        return output_files


def visualize_results(results_file=None, results_data=None):
    """Generate visualizations from performance test results."""
    visualizer = PerformanceVisualizer(results_file, results_data)
    return visualizer.generate_all_visualizations()


if __name__ == "__main__":
    # If run directly, visualize the most recent results file
    results_file = "chatbot_performance_metrics.json"
    if os.path.exists(results_file):
        visualize_results(results_file=results_file)
    else:
        print(f"Results file {results_file} not found. Run test_performance_metrics.py first.")
