#!/usr/bin/env python3
"""
Performance Test Suite Runner

This script runs the complete performance test suite for the chatbot,
generating metrics, visualizations, and a comprehensive report.
"""

import os
import sys
import time
import json
import shutil
from datetime import datetime
import argparse
import importlib.util

# Add project root directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Check for required packages
def check_dependencies():
    """Check if all required packages are installed."""
    missing_packages = []
    required_packages = {
        'numpy': 'Basic numerical operations',
        'matplotlib': 'Visualization of results',
        'memory_profiler': 'Memory usage tracking',
        'sklearn.metrics': 'Accuracy metrics calculation'
    }

    for package, description in required_packages.items():
        module_name = package.split('.')[0]  # Get base module name
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(f"{package} ({description})")

    return missing_packages

# Import test modules with dependency check
try:
    from chatbot_app.tests.test_performance_metrics import run_performance_tests
except ImportError as e:
    print(f"Error importing performance metrics module: {e}")
    print("Make sure required dependencies are installed by running:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Check if visualization dependencies are available before importing
visualization_available = importlib.util.find_spec('matplotlib') is not None
if visualization_available:
    try:
        from chatbot_app.tests.test_performance_visualization import visualize_results
    except ImportError as e:
        visualization_available = False
        print(f"Warning: Unable to import visualization module: {e}")
        print("Visualizations will be disabled.")
else:
    print("Warning: matplotlib not installed, visualizations will be disabled.")
    print("To enable visualizations, install matplotlib with:")
    print("pip install matplotlib")


def generate_html_report(results, visualization_paths):
    """
    Generate an HTML report with test results and visualizations.

    Args:
        results: Dictionary containing test results
        visualization_paths: Dictionary containing paths to visualization images

    Returns:
        Path to the generated HTML report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract summary data
    summary = results.get('summary', {})
    accuracy = summary.get('accuracy', {})
    latency = summary.get('latency', {})
    memory = summary.get('memory', {})
    coverage = summary.get('emotion_coverage', {})
    mixed = summary.get('mixed_emotions', {})
    benchmarks = summary.get('benchmarks', {})

    # Count passed benchmarks
    benchmarks_passed = sum([
        1 if benchmarks.get('accuracy_passed', False) else 0,
        1 if benchmarks.get('latency_passed', False) else 0,
        1 if benchmarks.get('memory_passed', False) else 0,
        1 if benchmarks.get('coverage_passed', False) else 0
    ])

    # Determine overall status
    if benchmarks_passed == 4:
        overall_status = "✅ All benchmarks passed"
        status_color = "green"
    elif benchmarks_passed >= 2:
        overall_status = f"⚠️ {benchmarks_passed}/4 benchmarks passed"
        status_color = "orange"
    else:
        overall_status = f"❌ {benchmarks_passed}/4 benchmarks passed"
        status_color = "red"

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Performance Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .status {{
            font-size: 24px;
            font-weight: bold;
            color: {status_color};
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            text-align: center;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .passed {{
            color: green;
            font-weight: bold;
        }}
        .failed {{
            color: red;
            font-weight: bold;
        }}
        .visualization {{
            margin: 30px 0;
            text-align: center;
        }}
        .visualization img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .metrics-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        .metric-card {{
            flex: 0 0 48%;
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .metric-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .benchmark {{
            display: inline-block;
            margin-left: 10px;
            font-size: 14px;
            padding: 2px 8px;
            border-radius: 3px;
        }}
        .executive-summary {{
            background-color: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 14px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <h1>Emotion-Aware Chatbot Performance Report</h1>
    <div class="timestamp">Generated on: {timestamp}</div>

    <div class="status">{overall_status}</div>

    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <p>
            This report presents the performance evaluation results of the Emotion-Aware Chatbot.
            The tests cover accuracy of emotion detection, processing latency, memory usage, and emotion class coverage.
            {benchmarks_passed} out of 4 benchmark targets were met in this test run.
        </p>
    </div>

    <h2>Benchmark Results</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Actual Value</th>
            <th>Target</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>Accuracy (F1-Score)</td>
            <td>{accuracy.get('f1_score', 0):.4f}</td>
            <td>{benchmarks.get('accuracy_target', 0):.2f}</td>
            <td class="{'passed' if benchmarks.get('accuracy_passed', False) else 'failed'}">
                {'PASSED' if benchmarks.get('accuracy_passed', False) else 'FAILED'}
            </td>
        </tr>
        <tr>
            <td>Latency (95th Percentile)</td>
            <td>{latency.get('p95_ms', 0):.2f} ms</td>
            <td>{benchmarks.get('latency_target_ms', 0)} ms</td>
            <td class="{'passed' if benchmarks.get('latency_passed', False) else 'failed'}">
                {'PASSED' if benchmarks.get('latency_passed', False) else 'FAILED'}
            </td>
        </tr>
        <tr>
            <td>Memory (Peak Usage)</td>
            <td>{memory.get('peak_mb', 0):.2f} MB</td>
            <td>{benchmarks.get('memory_target_mb', 0)} MB</td>
            <td class="{'passed' if benchmarks.get('memory_passed', False) else 'failed'}">
                {'PASSED' if benchmarks.get('memory_passed', False) else 'FAILED'}
            </td>
        </tr>
        <tr>
            <td>Emotion Coverage</td>
            <td>{coverage.get('rate', 0):.4f}</td>
            <td>{benchmarks.get('coverage_target', 0):.2f}</td>
            <td class="{'passed' if benchmarks.get('coverage_passed', False) else 'failed'}">
                {'PASSED' if benchmarks.get('coverage_passed', False) else 'FAILED'}
            </td>
        </tr>
    </table>

    <h2>Detailed Metrics</h2>

    <div class="metrics-container">
        <div class="metric-card">
            <div class="metric-title">Accuracy Metrics</div>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Precision</td>
                    <td>{results.get('accuracy', {}).get('precision', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Recall</td>
                    <td>{results.get('accuracy', {}).get('recall', 0):.4f}</td>
                </tr>
                <tr>
                    <td>F1-Score</td>
                    <td>{results.get('accuracy', {}).get('f1_score', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Direct Accuracy</td>
                    <td>{results.get('accuracy', {}).get('direct_accuracy', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Average Confidence</td>
                    <td>{results.get('accuracy', {}).get('average_confidence', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Test Cases</td>
                    <td>{results.get('accuracy', {}).get('test_cases', 0)}</td>
                </tr>
            </table>
        </div>

        <div class="metric-card">
            <div class="metric-title">Latency Metrics</div>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value (ms)</th>
                </tr>
                <tr>
                    <td>Minimum</td>
                    <td>{results.get('latency', {}).get('overall', {}).get('min', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Average</td>
                    <td>{results.get('latency', {}).get('overall', {}).get('avg', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Median</td>
                    <td>{results.get('latency', {}).get('overall', {}).get('median', 0):.2f}</td>
                </tr>
                <tr>
                    <td>95th Percentile</td>
                    <td>{results.get('latency', {}).get('overall', {}).get('p95', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Maximum</td>
                    <td>{results.get('latency', {}).get('overall', {}).get('max', 0):.2f}</td>
                </tr>
            </table>
        </div>

        <div class="metric-card">
            <div class="metric-title">Memory Usage</div>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value (MB)</th>
                </tr>
                <tr>
                    <td>Baseline</td>
                    <td>{results.get('memory_usage', {}).get('baseline_mb', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Average</td>
                    <td>{results.get('memory_usage', {}).get('average_mb', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Peak</td>
                    <td>{results.get('memory_usage', {}).get('peak_mb', 0):.2f}</td>
                </tr>
                <tr>
                    <td>Increase</td>
                    <td>{results.get('memory_usage', {}).get('increase_mb', 0):.2f}</td>
                </tr>
            </table>
        </div>

        <div class="metric-card">
            <div class="metric-title">Mixed Emotion Detection</div>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Full Matches</td>
                    <td>{results.get('mixed_emotion_detection', {}).get('full_matches', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Partial Matches</td>
                    <td>{results.get('mixed_emotion_detection', {}).get('partial_matches', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Average Coverage</td>
                    <td>{results.get('mixed_emotion_detection', {}).get('average_coverage', 0):.4f}</td>
                </tr>
                <tr>
                    <td>Test Cases</td>
                    <td>{results.get('mixed_emotion_detection', {}).get('test_cases', 0)}</td>
                </tr>
            </table>
        </div>
    </div>

    <h2>Emotion Class Coverage</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Total Emotion Classes</td>
            <td>{results.get('emotion_coverage', {}).get('total_emotions', 0)}</td>
        </tr>
        <tr>
            <td>Detected Emotion Classes</td>
            <td>{results.get('emotion_coverage', {}).get('detected_emotions', 0)}</td>
        </tr>
        <tr>
            <td>Coverage Rate</td>
            <td>{results.get('emotion_coverage', {}).get('coverage_rate', 0):.4f}</td>
        </tr>
        <tr>
            <td>Missing Emotions</td>
            <td>{', '.join(results.get('emotion_coverage', {}).get('missing_emotions', []))}</td>
        </tr>
    </table>

    <h2>Visualizations</h2>
"""

    # Add visualizations
    if visualization_paths and any(path and os.path.exists(path) for _, path in visualization_paths.items()):
        for name, path in visualization_paths.items():
            if path and os.path.exists(path):
                title = name.replace('_', ' ').title()
                rel_path = os.path.basename(path)
                html_content += f"""
    <div class="visualization">
        <h3>{title}</h3>
        <img src="{rel_path}" alt="{title}" />
    </div>
    """
    else:
        html_content += f"""
    <div class="visualization">
        <h3>Visualizations Not Available</h3>
        <p>Visualizations could not be generated due to missing dependencies.</p>
        <p>Install matplotlib and other visualization packages to enable this feature:</p>
        <pre>pip install matplotlib numpy scikit-learn</pre>
    </div>
"""

    # Add footer
    html_content += f"""
    <footer>
        <p>Emotion-Aware Chatbot Performance Test Suite &copy; {datetime.now().year}</p>
    </footer>
</body>
</html>
"""

    # Create report directory
    report_dir = "performance_report"
    os.makedirs(report_dir, exist_ok=True)

    # Copy visualization files to report directory
    for name, path in visualization_paths.items():
        if path and os.path.exists(path):
            shutil.copy(path, os.path.join(report_dir, os.path.basename(path)))

    # Write the HTML report
    report_path = os.path.join(report_dir, "performance_report.html")
    with open(report_path, 'w') as f:
        f.write(html_content)

    print(f"HTML report generated: {os.path.abspath(report_path)}")
    return report_path


def run_performance_suite(output_format='all'):
    """
    Run the complete performance test suite and generate reports.

    Args:
        output_format: Format for output ('json', 'html', 'visualizations', 'all')

    Returns:
        Dictionary with paths to generated output files
    """
    # Check for missing dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print("Warning: Some functionality may be limited due to missing packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages to enable full functionality:")
        print("pip install -r requirements.txt")
        print("\nContinuing with available features...\n")

    start_time = time.time()
    print("=" * 80)
    print("Starting Emotion-Aware Chatbot Performance Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Run performance tests
    print("\nRunning performance metrics tests...")
    results, json_file = run_performance_tests()

    output_files = {'json': json_file}
    visualization_paths = {}

    # Generate visualizations if requested and available
    if output_format in ['visualizations', 'all', 'html'] and visualization_available:
        print("\nGenerating visualizations...")
        try:
            visualization_paths = visualize_results(results_data=results)
            output_files['visualizations'] = visualization_paths
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            print("Continuing without visualizations...")
    elif output_format in ['visualizations', 'all', 'html'] and not visualization_available:
        print("\nSkipping visualizations due to missing dependencies.")
        print("Install matplotlib to enable visualization features.")

    # Generate HTML report if requested
    if output_format in ['html', 'all']:
        print("\nGenerating HTML report...")
        try:
            html_report = generate_html_report(results, visualization_paths)
            output_files['html'] = html_report
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            print("Continuing without HTML report...")

    # Print execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nPerformance test suite completed in {execution_time:.2f} seconds")

    # Print summary
    summary = results.get('summary', {})
    benchmarks = summary.get('benchmarks', {})
    benchmarks_passed = sum([
        1 if benchmarks.get('accuracy_passed', False) else 0,
        1 if benchmarks.get('latency_passed', False) else 0,
        1 if benchmarks.get('memory_passed', False) else 0,
        1 if benchmarks.get('coverage_passed', False) else 0
    ])

    print("\nBenchmark Results Summary:")
    print(f"  - Accuracy (F1-Score): {summary.get('accuracy', {}).get('f1_score', 0):.4f} "
          f"({'PASSED' if benchmarks.get('accuracy_passed', False) else 'FAILED'})")
    print(f"  - Latency (95th Percentile): {summary.get('latency', {}).get('p95_ms', 0):.2f} ms "
          f"({'PASSED' if benchmarks.get('latency_passed', False) else 'FAILED'})")
    print(f"  - Memory (Peak Usage): {summary.get('memory', {}).get('peak_mb', 0):.2f} MB "
          f"({'PASSED' if benchmarks.get('memory_passed', False) else 'FAILED'})")
    print(f"  - Emotion Coverage: {summary.get('emotion_coverage', {}).get('rate', 0):.4f} "
          f"({'PASSED' if benchmarks.get('coverage_passed', False) else 'FAILED'})")
    print(f"\nOverall: {benchmarks_passed}/4 benchmarks passed")

    if output_format in ['html', 'all']:
        print(f"\nDetailed report available at: {os.path.abspath(output_files['html'])}")

    return output_files


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Run emotion chatbot performance test suite')
        parser.add_argument('--format', choices=['json', 'html', 'visualizations', 'all'], 
                            default='all', help='Output format')
        parser.add_argument('--open-report', action='store_true',
                            help='Open the HTML report in the default browser after generation')
        parser.add_argument('--skip-missing', action='store_true',
                            help='Skip tests that require missing dependencies')

        args = parser.parse_args()

        output_files = run_performance_suite(output_format=args.format)

        # Open the HTML report in the default browser if requested
        if args.open_report and 'html' in output_files and os.path.exists(output_files['html']):
            try:
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(output_files['html']))
                print(f"Opened HTML report in browser: {output_files['html']}")
            except ImportError:
                print(f"Could not open browser, report is available at: {output_files['html']}")

        print("\nPerformance test suite completed successfully!")

    except KeyboardInterrupt:
        print("\nTest suite interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running performance test suite: {e}")
        import traceback
        traceback.print_exc()
        print("\nSome tests may have completed. Check the output directory for partial results.")
        sys.exit(1)
