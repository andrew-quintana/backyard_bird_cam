#!/usr/bin/env python3
"""
Simple PIR-Triggered Camera

Takes high-resolution photos when motion is detected by the PIR sensor.
Uses auto/default settings for simple testing.
"""

import os
import time
import argparse
import subprocess
import datetime
import pigpio
import signal
import sys

# Default settings
DEFAULT_OUTPUT_DIR = "data/photos"
DEFAULT_PIR_PIN = 4
DEFAULT_COOLDOWN = 3  # seconds between photos

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit cleanly"""
    print("\nExiting the PIR trigger program.")
    sys.exit(0)

def capture_photo(output_dir, filename):
    """Capture a high-resolution photo with auto settings"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, filename)
    
    # Simple command with max resolution and auto settings
    cmd = [
        "libcamera-still", 
        "-o", output_path,
        "--width", "4056",     # Maximum width
        "--height", "3040",    # Maximum height
        "--quality", "100",    # Maximum quality
        "--immediate"          # Don't wait for auto-convergence
    ]
    
    # Run the command
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            print(f"Photo captured: {output_path}")
            return True
        else:
            print(f"Error capturing photo: {process.stderr}")
            return False
    except Exception as e:
        print(f"Exception while capturing photo: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple PIR-triggered photo capture")
    
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory for photos (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--pin", "-p", type=int, default=DEFAULT_PIR_PIN,
                        help=f"GPIO pin number for PIR sensor (default: {DEFAULT_PIR_PIN})")
    parser.add_argument("--cooldown", "-c", type=float, default=DEFAULT_COOLDOWN,
                        help=f"Cooldown time between photos in seconds (default: {DEFAULT_COOLDOWN}s)")
    parser.add_argument("--test", action="store_true",
                        help="Take a test photo and exit (no PIR trigger)")
    
    args = parser.parse_args()
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Take a test photo if requested
    if args.test:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_{timestamp}.jpg"
        capture_photo(args.output, filename)
        print(f"Test photo saved to {os.path.join(args.output, filename)}")
        return
    
    # Connect to the pigpio daemon
    print("Connecting to pigpio daemon...")
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon. Make sure it's running:")
        print("  sudo pigpiod")
        return
    
    # Set up the PIR pin
    pi.set_mode(args.pin, pigpio.INPUT)
    
    # Initialize variables
    last_motion_time = 0
    last_state = pi.read(args.pin)
    photo_count = 0
    
    print(f"PIR-triggered photo capture started.")
    print(f"Using pin GPIO{args.pin} for motion detection")
    print(f"Photos will be saved to: {os.path.abspath(args.output)}")
    print(f"Maximum resolution photos (4056x3040)")
    print(f"Cooldown between photos: {args.cooldown}s")
    print("Press Ctrl+C to exit")
    
    # Small warm-up time for the PIR sensor
    print("Warming up PIR sensor (5 seconds)...")
    time.sleep(5)
    print("Ready to detect motion!")
    
    try:
        while True:
            # Read current state
            current_state = pi.read(args.pin)
            current_time = time.time()
            
            # Print state changes for debugging
            if current_state != last_state:
                state_name = "HIGH (1)" if current_state == 1 else "LOW (0)"
                print(f"PIR state changed to {state_name}")
            
            # Check if motion was detected (rising edge: 0->1) and past cooldown period
            if current_state == 1 and last_state == 0 and (current_time - last_motion_time > args.cooldown):
                # Motion detected, take a photo
                print("Motion detected! Capturing photo...")
                
                # Create filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"motion_{timestamp}.jpg"
                
                if capture_photo(args.output, filename):
                    photo_count += 1
                    last_motion_time = current_time
                
            # Update last state
            last_state = current_state
            
            # Short delay to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        if pi.connected:
            pi.stop()
        print(f"Total photos captured: {photo_count}")

if __name__ == "__main__":
    main() 