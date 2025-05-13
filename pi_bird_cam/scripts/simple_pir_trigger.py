#!/usr/bin/env python3
"""
Smart PIR-Triggered Bird Camera

Takes high-resolution photos when motion is detected by the PIR sensor.
Features:
- Always-active camera for fastest response time
- Burst mode: Captures multiple photos when motion is detected
- Configurable PIR sampling rate for adjustable sensitivity
- Comprehensive logging system
"""

import os
import time
import argparse
import subprocess
import datetime
import pigpio
import signal
import sys
import logging
import logging.handlers
from pi_bird_cam.camera.camera_handler import CameraHandler
import RPi.GPIO as GPIO

# Configure logging
def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'DEBUG')
    log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # File handler for persistent logs
    log_file = os.path.join(log_dir, f'bird_camera_{datetime.datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    
    # Console handler for immediate output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)
    
    # Log system information
    logging.info("=== Bird Camera Service Starting ===")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info(f"User: {os.getuid()}")
    logging.info(f"Group: {os.getgid()}")
    logging.info(f"Environment: {dict(os.environ)}")
    logging.info("=== System Information Logged ===")

# Call setup_logging at the start of the script
setup_logging()

# Default settings
DEFAULT_OUTPUT_DIR = "data/photos"
DEFAULT_PIR_PIN = 4
# Cooldown = (BURST_COUNT × BURST_DELAY) + SAFETY_BUFFER
# Example: (5 × 0.3) + 0.2 = 1.7 seconds
DEFAULT_BURST_COUNT = 5  # number of photos in burst
DEFAULT_BURST_DELAY = 0.3  # seconds between burst photos
DEFAULT_SAMPLING_RATE = 0.1  # seconds between PIR sensor checks
DEFAULT_COOLDOWN = (DEFAULT_BURST_COUNT * DEFAULT_BURST_DELAY) + 0.2  # seconds between motion triggers

# Global camera variable
camera = None

def initialize_camera():
    """Initialize the camera and keep it active"""
    global camera
    try:
        camera = CameraHandler(
            resolution=(4056, 3040),
            rotation=0,
            focus_distance_inches=24  # Default focus distance
        )
        camera.setup()
        logging.info("Camera initialized and active")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize camera: {e}")
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
        camera.take_photo(output_path)
        logging.info(f"Photo captured: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Exception while capturing photo: {e}")
        # Try to recover by reinitializing the camera
        try:
            if camera:
                camera.cleanup()
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
            camera.cleanup()
            camera = None
        GPIO.cleanup()
    except:
        pass
    logging.info("Cleanup complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals"""
    logging.info("Exiting...")
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
        logging.info(f"Taking test burst of {args.burst} photos...")
        capture_burst(args.output, "test", args.burst, args.burst_delay)
        logging.info(f"Test photos saved to {os.path.abspath(args.output)}")
        return
    
    # Connect to the pigpio daemon
    logging.info("Connecting to pigpio daemon...")
    pi = pigpio.pi()
    if not pi.connected:
        logging.error("Failed to connect to pigpio daemon. Make sure it's running:")
        logging.error("  sudo pigpiod")
        return
    
    # Set up the PIR pin
    pi.set_mode(args.pin, pigpio.INPUT)
    
    # Initialize variables
    last_motion_time = 0
    last_state = pi.read(args.pin)
    photo_count = 0
    
    logging.info(f"PIR-triggered photo capture started.")
    logging.info(f"Using pin GPIO{args.pin} for motion detection")
    logging.info(f"Photos will be saved to: {os.path.abspath(args.output)}")
    logging.info(f"Maximum resolution photos (4056x3040)")
    logging.info(f"Burst mode: {args.burst} photos with {args.burst_delay}s delay")
    logging.info(f"Cooldown between triggers: {args.cooldown}s")
    logging.info(f"PIR sensor sampling rate: {args.sampling_rate}s")
    logging.info("Camera kept always active for fastest response")
    logging.info("Press Ctrl+C to exit")
    
    # Small warm-up time for the PIR sensor
    logging.info("Warming up PIR sensor (5 seconds)...")
    time.sleep(5)
    logging.info("Ready to detect motion!")
    
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
                logging.debug(f"PIR state changed to {state_name}")
            
            # Check if motion was detected (rising edge: 0->1) and past cooldown period
            if current_state == 1 and last_state == 0 and (current_time - last_motion_time > args.cooldown):
                # Motion detected, take a burst of photos
                logging.info(f"Motion detected! Capturing burst of {args.burst} photos...")
                
                # Capture the burst
                successful = capture_burst(args.output, "motion", args.burst, args.burst_delay)
                photo_count += successful
                
                if successful > 0:
                    logging.info(f"Burst complete: {successful}/{args.burst} photos captured")
                    last_motion_time = current_time
                else:
                    logging.error("Failed to capture any photos in burst")
                
            # Update last state
            last_state = current_state
            
            # Delay between PIR sensor checks (sampling rate)
            time.sleep(args.sampling_rate)
            
    except KeyboardInterrupt:
        logging.info("\nProgram stopped by user")
    finally:
        if pi.connected:
            pi.stop()
        cleanup()
        logging.info(f"Total photos captured: {photo_count}")

if __name__ == "__main__":
    main() 