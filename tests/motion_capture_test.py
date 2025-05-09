#!/usr/bin/env python3
"""
Test script that combines PIR motion detection with camera capture.
This is a simplified version of the main application for testing purposes.
"""
import pigpio
import time
import os
import datetime
import subprocess
import argparse
from pathlib import Path

def log_event(message):
    """Log a message to console with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

def take_photo(output_dir="data/photos", prefix="test"):
    """Capture a photo using libcamera."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{prefix}_{timestamp}.jpg"
    
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Capture photo using libcamera-still
    cmd = f"libcamera-still -o {filename} --immediate"
    log_event(f"Capturing photo: {filename}")
    subprocess.run(cmd, shell=True)
    log_event(f"Photo saved: {filename}")
    
    return filename

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PIR Motion Detection and Camera Test')
    parser.add_argument('--pin', type=int, default=4, help='GPIO pin number (default: 4)')
    parser.add_argument('--time', type=int, default=60, help='Duration in seconds (default: 60)')
    parser.add_argument('--output', type=str, default='data/photos', help='Output directory (default: data/photos)')
    parser.add_argument('--cooldown', type=int, default=5, help='Cooldown time between captures in seconds (default: 5)')
    parser.add_argument('--test-only', action='store_true', help='Only take a test photo and exit')
    args = parser.parse_args()
    
    # Get parameters
    PIR_PIN = args.pin
    DURATION = args.time
    PHOTO_DIR = args.output
    COOLDOWN_TIME = args.cooldown
    
    log_event("Starting PIR motion detection and camera test")
    log_event(f"Using GPIO pin {PIR_PIN}")
    log_event(f"Photos will be saved to {os.path.abspath(PHOTO_DIR)}")
    
    # Take an initial test photo
    log_event("Taking initial test photo...")
    test_photo = take_photo(PHOTO_DIR, "init_test")
    
    # If only testing the camera, exit here
    if args.test_only:
        log_event("Camera test complete. Exiting.")
        return
    
    log_event(f"Test will run for {DURATION} seconds")
    log_event(f"Cooldown between photos: {COOLDOWN_TIME} seconds")
    
    # Connect to pigpio daemon
    pi = pigpio.pi()
    if not pi.connected:
        log_event("Failed to connect to pigpio daemon. Try running: sudo systemctl start pigpiod")
        return
    
    # Set pin mode
    pi.set_mode(PIR_PIN, pigpio.INPUT)
    
    log_event("PIR sensor initialized successfully")
    log_event("Sensor warming up (5 seconds)...")
    
    # Give the PIR sensor a short time to stabilize (shortened for testing)
    time.sleep(5)
    
    log_event("System ready - Monitoring for motion")
    
    # Record start time
    start_time = time.time()
    end_time = start_time + DURATION
    last_motion_time = 0
    last_state = pi.read(PIR_PIN)
    photo_count = 0
    
    try:
        while time.time() < end_time:
            # Read the current state
            current_state = pi.read(PIR_PIN)
            
            # Check if motion was detected (rising edge: 0->1)
            if current_state == 1 and last_state == 0:
                current_time = time.time()
                
                # Check if we're past the cooldown period
                if current_time - last_motion_time > COOLDOWN_TIME:
                    log_event("Motion detected!")
                    photo_path = take_photo(PHOTO_DIR, "motion")
                    last_motion_time = current_time
                    photo_count += 1
                else:
                    log_event(f"Motion detected but within cooldown period ({COOLDOWN_TIME}s)")
            
            # Update last state
            last_state = current_state
            
            # Small delay to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        log_event("Test stopped by user")
    except Exception as e:
        log_event(f"Error: {e}")
    finally:
        # Clean up
        if pi.connected:
            pi.stop()
        
        # Summary
        elapsed = time.time() - start_time
        log_event(f"Test completed. Duration: {elapsed:.1f} seconds")
        log_event(f"Total photos captured: {photo_count}")

if __name__ == "__main__":
    main() 