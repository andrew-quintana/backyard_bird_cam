#!/usr/bin/env python3
"""
PIR-Triggered Photo Capture

This script captures photos when motion is detected by the PIR sensor.
It allows configuring different camera parameters for optimal bird photography.
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
DEFAULT_COOLDOWN = 5  # seconds between photos

# Common camera profiles for different lighting conditions
CAMERA_PROFILES = {
    "default": "--ev 0 --sharpness 1.0 --contrast 1.0 --brightness 0.0 --saturation 1.0 --quality 90 --immediate",
    "daylight": "--ev 0 --awb daylight --sharpness 1.2 --contrast 1.1 --brightness 0.0 --saturation 1.1 --quality 90 --immediate",
    "cloudy": "--ev 0.3 --awb cloudy --sharpness 1.2 --contrast 1.0 --brightness 0.1 --saturation 1.2 --quality 90 --immediate",
    "lowlight": "--shutter 10000 --gain 2.0 --awb indoor --brightness 0.1 --quality 90 --immediate",
    "action": "--shutter 2000 --gain 1.5 --awb auto --sharpness 1.2 --quality 90 --immediate",
}

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit cleanly"""
    print("\nExiting the photo capture program.")
    sys.exit(0)

def capture_photo(output_dir, filename, width, height, camera_params):
    """Capture a photo with the given parameters"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, filename)
    
    # Build the command
    cmd = ["libcamera-still", "-o", output_path]
    
    # Add resolution parameters
    if width and height:
        cmd.extend(["--width", str(width), "--height", str(height)])
    
    # Add other camera parameters
    cmd.extend(camera_params.split())
    
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
    parser = argparse.ArgumentParser(description="PIR-triggered photo capture")
    
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory for photos (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--pin", "-p", type=int, default=DEFAULT_PIR_PIN,
                        help=f"GPIO pin number for PIR sensor (default: {DEFAULT_PIR_PIN})")
    parser.add_argument("--width", "-w", type=int, default=2028,
                        help="Photo width in pixels (default: 2028)")
    parser.add_argument("--height", "-h", type=int, default=1520,
                        help="Photo height in pixels (default: 1520)")
    parser.add_argument("--cooldown", "-c", type=float, default=DEFAULT_COOLDOWN,
                        help=f"Cooldown time between photos in seconds (default: {DEFAULT_COOLDOWN}s)")
    parser.add_argument("--profile", choices=list(CAMERA_PROFILES.keys()), default="default",
                        help="Camera profile to use (default: default)")
    parser.add_argument("--custom", help="Custom camera parameters (overrides profile)")
    parser.add_argument("--prefix", default="bird_",
                        help="Filename prefix for captured photos (default: bird_)")
    parser.add_argument("--test", action="store_true",
                        help="Take a test photo and exit")
    
    args = parser.parse_args()
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get camera parameters
    camera_params = args.custom if args.custom else CAMERA_PROFILES[args.profile]
    
    # Take a test photo if requested
    if args.test:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{args.prefix}test_{timestamp}.jpg"
        capture_photo(args.output, filename, args.width, args.height, camera_params)
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
    print(f"Camera profile: {args.profile}")
    print(f"Resolution: {args.width}x{args.height}")
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
            
            # Check if motion was detected (rising edge: 0->1) and past cooldown period
            if current_state == 1 and last_state == 0 and (current_time - last_motion_time > args.cooldown):
                # Motion detected, take a photo
                print("Motion detected! Capturing photo...")
                
                # Create filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{args.prefix}{timestamp}.jpg"
                
                if capture_photo(args.output, filename, args.width, args.height, camera_params):
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