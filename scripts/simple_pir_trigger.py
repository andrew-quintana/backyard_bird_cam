#!/usr/bin/env python3
"""
Smart PIR-Triggered Bird Camera

Takes high-resolution photos when motion is detected by the PIR sensor.
Features:
- Always-active camera for fastest response time
- Burst mode: Captures multiple photos when motion is detected
- Configurable PIR sampling rate for adjustable sensitivity
"""

import os
import time
import argparse
import subprocess
import datetime
import pigpio
import signal
import sys
from picamera2 import Picamera2
from libcamera import controls
import RPi.GPIO as GPIO

# Default settings
DEFAULT_OUTPUT_DIR = "data/photos"
DEFAULT_PIR_PIN = 4
DEFAULT_COOLDOWN = 0  # seconds between motion triggers
DEFAULT_BURST_COUNT = 3  # number of photos in burst
DEFAULT_BURST_DELAY = 0.5  # seconds between burst photos
DEFAULT_SAMPLING_RATE = 0.1  # seconds between PIR sensor checks

# Global camera variable
camera = None

def initialize_camera():
    """Initialize the camera and keep it active"""
    global camera
    try:
        camera = Picamera2()
        # Configure for high resolution still capture
        still_config = camera.create_still_configuration(
            main={"size": (4056, 3040)},
            lores={"size": (640, 480)},
            display="lores"
        )
        camera.configure(still_config)
        
        # Start the camera and keep it active
        camera.start(show_preview=False)
        
        # Apply initial settings
        camera.set_controls({
            "AfMode": controls.AfModeEnum.Continuous,
            "AwbMode": controls.AwbModeEnum.Auto,
            "AeEnable": True
        })
        
        print("Camera initialized and active")
        return True
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        return False

def capture_photo(output_dir, filename):
    """Capture a high-resolution photo with the always-active camera"""
    global camera
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, filename)
    
    try:
        # Make sure camera is initialized
        if camera is None:
            if not initialize_camera():
                return False
        
        # Capture photo
        camera.capture_file(output_path)
        print(f"Photo captured: {output_path}")
        return True
    except Exception as e:
        print(f"Exception while capturing photo: {e}")
        # Try to recover by reinitializing the camera
        try:
            if camera:
                camera.close()
            camera = None
            initialize_camera()
        except:
            pass
        return False

def capture_burst(output_dir, base_filename, count, delay):
    """Capture a burst of photos in sequence"""
    successful_captures = 0
    
    # Use timestamp as the base for all files in burst
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i in range(count):
        # Create filename with burst index
        filename = f"{timestamp}_burst{i+1}.jpg"
            
        # Capture the photo
        if capture_photo(output_dir, filename):
            successful_captures += 1
        
        # Wait between burst photos, but not after the last one
        if i < count - 1:
            time.sleep(delay)
    
    return successful_captures

def cleanup():
    """Clean up resources properly"""
    global camera
    try:
        if camera:
            camera.close()
            camera = None
        GPIO.cleanup()
    except:
        pass
    print("Cleanup complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals"""
    print("Exiting...")
    cleanup()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Smart PIR-triggered bird camera")
    
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory for photos (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--pin", "-p", type=int, default=DEFAULT_PIR_PIN,
                        help=f"GPIO pin number for PIR sensor (default: {DEFAULT_PIR_PIN})")
    parser.add_argument("--cooldown", "-c", type=float, default=DEFAULT_COOLDOWN,
                        help=f"Cooldown time between motion triggers in seconds (default: {DEFAULT_COOLDOWN}s)")
    parser.add_argument("--burst", "-b", type=int, default=DEFAULT_BURST_COUNT,
                        help=f"Number of photos to take in burst mode (default: {DEFAULT_BURST_COUNT})")
    parser.add_argument("--burst-delay", "-bd", type=float, default=DEFAULT_BURST_DELAY,
                        help=f"Delay between burst photos in seconds (default: {DEFAULT_BURST_DELAY}s)")
    parser.add_argument("--sampling-rate", "-sr", type=float, default=DEFAULT_SAMPLING_RATE,
                        help=f"How often to check PIR sensor in seconds (default: {DEFAULT_SAMPLING_RATE}s)")
    parser.add_argument("--test", action="store_true",
                        help="Take a test burst and exit (no PIR trigger)")
    
    args = parser.parse_args()
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Take a test photo if requested
    if args.test:
        print(f"Taking test burst of {args.burst} photos...")
        capture_burst(args.output, "test", args.burst, args.burst_delay)
        print(f"Test photos saved to {os.path.abspath(args.output)}")
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
    print(f"Burst mode: {args.burst} photos with {args.burst_delay}s delay")
    print(f"Cooldown between triggers: {args.cooldown}s")
    print(f"PIR sensor sampling rate: {args.sampling_rate}s")
    print("Camera kept always active for fastest response")
    print("Press Ctrl+C to exit")
    
    # Small warm-up time for the PIR sensor
    print("Warming up PIR sensor (5 seconds)...")
    time.sleep(5)
    print("Ready to detect motion!")
    
    try:
        # Initialize camera and keep it active
        initialize_camera()
        
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
                # Motion detected, take a burst of photos
                print(f"Motion detected! Capturing burst of {args.burst} photos...")
                
                # Capture the burst
                successful = capture_burst(args.output, "motion", args.burst, args.burst_delay)
                photo_count += successful
                
                if successful > 0:
                    print(f"Burst complete: {successful}/{args.burst} photos captured")
                    last_motion_time = current_time
                else:
                    print("Failed to capture any photos in burst")
                
            # Update last state
            last_state = current_state
            
            # Delay between PIR sensor checks (sampling rate)
            time.sleep(args.sampling_rate)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        if pi.connected:
            pi.stop()
        cleanup()
        print(f"Total photos captured: {photo_count}")

if __name__ == "__main__":
    main() 