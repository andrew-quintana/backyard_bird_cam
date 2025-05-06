#!/usr/bin/env python3
"""PIR Sensor Data Analysis Tool.

This script analyzes CSV data from the PIR sensor calibration tool to help
determine optimal thresholds and settings.
"""
import argparse
import sys
import csv
from collections import defaultdict


def analyze_data(file_path, window_sizes):
    """Analyze PIR sensor data with different sliding window sizes.
    
    Args:
        file_path (str): Path to the CSV file with timestamp,value columns
        window_sizes (list): List of window sizes in seconds to analyze
    """
    # Read the data from CSV
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'timestamp': float(row['timestamp']),
                'value': int(row['value'])
            })
    
    if not data:
        print("No data found in the file.")
        return
    
    # Basic statistics
    total_samples = len(data)
    ones_count = sum(1 for d in data if d['value'] == 1)
    zeros_count = total_samples - ones_count
    
    print(f"Total samples: {total_samples}")
    print(f"High signals (1): {ones_count} ({ones_count/total_samples*100:.2f}%)")
    print(f"Low signals (0): {zeros_count} ({zeros_count/total_samples*100:.2f}%)")
    print()
    
    # Duration analysis
    durations = []
    current_value = None
    start_time = None
    
    for i, d in enumerate(data):
        if current_value is None:
            current_value = d['value']
            start_time = d['timestamp']
        elif d['value'] != current_value:
            durations.append({
                'value': current_value,
                'duration': d['timestamp'] - start_time,
                'start': start_time,
                'end': d['timestamp']
            })
            current_value = d['value']
            start_time = d['timestamp']
            
    # Add the last segment
    if start_time is not None and data:
        durations.append({
            'value': current_value,
            'duration': data[-1]['timestamp'] - start_time,
            'start': start_time,
            'end': data[-1]['timestamp']
        })
    
    # Calculate statistics for high and low signal durations
    high_durations = [d['duration'] for d in durations if d['value'] == 1]
    low_durations = [d['duration'] for d in durations if d['value'] == 0]
    
    if high_durations:
        avg_high = sum(high_durations) / len(high_durations)
        max_high = max(high_durations)
        min_high = min(high_durations)
        print(f"High signal durations (seconds):")
        print(f"  Min: {min_high:.2f}")
        print(f"  Avg: {avg_high:.2f}")
        print(f"  Max: {max_high:.2f}")
    else:
        print("No high signals detected.")
    
    if low_durations:
        avg_low = sum(low_durations) / len(low_durations)
        max_low = max(low_durations)
        min_low = min(low_durations)
        print(f"Low signal durations (seconds):")
        print(f"  Min: {min_low:.2f}")
        print(f"  Avg: {avg_low:.2f}")
        print(f"  Max: {max_low:.2f}")
    else:
        print("No low signals detected.")
    
    print()
    
    # Window analysis for different time windows
    for window in window_sizes:
        print(f"=== Analysis for {window:.1f} second window ===")
        
        # Create windows
        start_time = data[0]['timestamp']
        end_time = data[-1]['timestamp']
        
        windows = defaultdict(list)
        for d in data:
            window_index = int((d['timestamp'] - start_time) / window)
            windows[window_index].append(d)
        
        # Analyze each window
        motion_windows = 0
        
        for idx, window_data in sorted(windows.items()):
            high_count = sum(1 for d in window_data if d['value'] == 1)
            window_start = start_time + idx * window
            window_end = window_start + window
            
            # Only count windows with at least one high value
            if high_count > 0:
                motion_windows += 1
                high_percent = (high_count / len(window_data)) * 100
                print(f"Window {idx} ({window_start:.2f} - {window_end:.2f}s): "
                      f"{high_count}/{len(window_data)} high signals ({high_percent:.2f}%)")
        
        print(f"Total windows with motion: {motion_windows}/{len(windows)}")
        print()


def main():
    """Main function for PIR data analysis."""
    parser = argparse.ArgumentParser(description='PIR Sensor Data Analysis Tool')
    parser.add_argument('file', type=str, help='Path to the CSV file with PIR sensor data')
    parser.add_argument('--windows', type=float, nargs='+', default=[0.5, 1.0, 2.0, 5.0],
                        help='Window sizes in seconds for analysis')
    args = parser.parse_args()
    
    try:
        analyze_data(args.file, args.windows)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 