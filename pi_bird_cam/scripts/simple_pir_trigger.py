#!/usr/bin/env python3
"""
Smart PIR-Triggered Bird Camera

Takes high-resolution photos when motion is detected by the PIR sensor.
Features:
- Always-active camera for fastest response time
- Burst mode: Captures multiple photos when motion is detected
- Configurable PIR sampling rate for adjustable sensitivity
- Comprehensive logging system
- Time-based activation (only active during specified hours)
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
# Default time range (5am to 9am PST)
DEFAULT_TIME_RANGE_ENABLED = True
DEFAULT_START_HOUR = 5
DEFAULT_START_MINUTE = 0
DEFAULT_END_HOUR = 9
DEFAULT_END_MINUTE = 0

# Global camera variable
camera = None

def initialize_camera():
    """Initialize the camera and keep it active"""
    global camera
    try:
        # Clean up any existing camera instance
        if camera:
            camera.cleanup()
            camera = None
            time.sleep(0.5)  # Give time for resources to be fully released
            
        camera = CameraHandler(
            resolution=(4056, 3040),
            rotation=0,
            focus_distance_inches=13.5  # Default focus distance
        )
        camera.setup()
        logging.info("Camera initialized and active")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize camera: {e}")
        if camera:
            try:
                camera.cleanup()
            except:
                pass
            camera = None
        return False

def capture_photo(output_dir, filename):
    """Capture a high-resolution photo with the always-active camera"""
    global camera
    
    # Ensure the base output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create date-based directory
    date_dir = datetime.datetime.now().strftime("%Y%m%d")
    date_dir_path = os.path.join(output_dir, date_dir)
    
    # Ensure date directory exists
    os.makedirs(date_dir_path, exist_ok=True)
    
    # Full path for the photo
    output_path = os.path.join(date_dir_path, filename)
    
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
            time.sleep(0.5)  # Give time for resources to be fully released
            initialize_camera()
        except:
            pass
        return False

def capture_burst(output_dir, base_filename, count, delay):
    """Capture a burst of photos in sequence"""
    successful_captures = 0
    
    # Use timestamp as the base for all files in burst
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create date-based directory name
    date_dir = datetime.datetime.now().strftime("%Y%m%d")
    date_dir_path = os.path.join(output_dir, date_dir)
    
    # Ensure date directory exists
    os.makedirs(date_dir_path, exist_ok=True)
    
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
            time.sleep(0.5)  # Give time for resources to be fully released
        GPIO.cleanup()
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    logging.info("Cleanup complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals"""
    logging.info("Exiting...")
    cleanup()
    sys.exit(0)

def is_time_in_range(start_hour, start_minute, end_hour, end_minute):
    """Check if current time is within the specified range.
    
    Args:
        start_hour (int): Starting hour (0-23)
        start_minute (int): Starting minute (0-59)
        end_hour (int): Ending hour (0-23)
        end_minute (int): Ending minute (0-59)
        
    Returns:
        bool: True if current time is within range, False otherwise
    """
    now = datetime.datetime.now()
    current_hour, current_minute = now.hour, now.minute
    
    # Convert times to minutes for easier comparison
    start_time = start_hour * 60 + start_minute
    end_time = end_hour * 60 + end_minute
    current_time = current_hour * 60 + current_minute
    
    # Handle ranges that cross midnight
    if end_time < start_time:
        return current_time >= start_time or current_time <= end_time
    else:
        return start_time <= current_time <= end_time

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
    
    # Time range arguments
    parser.add_argument("--time-range", action="store_true", default=DEFAULT_TIME_RANGE_ENABLED,
                        help="Enable time-based activation (default: enabled)")
    parser.add_argument("--no-time-range", action="store_false", dest="time_range",
                        help="Disable time-based activation")
    parser.add_argument("--start-time", type=str, default=f"{DEFAULT_START_HOUR:02d}:{DEFAULT_START_MINUTE:02d}",
                        help=f"Start time in 24-hour format HH:MM (default: {DEFAULT_START_HOUR:02d}:{DEFAULT_START_MINUTE:02d})")
    parser.add_argument("--end-time", type=str, default=f"{DEFAULT_END_HOUR:02d}:{DEFAULT_END_MINUTE:02d}",
                        help=f"End time in 24-hour format HH:MM (default: {DEFAULT_END_HOUR:02d}:{DEFAULT_END_MINUTE:02d})")
    
    args = parser.parse_args()
    
    # Parse time range arguments
    try:
        start_hour, start_minute = map(int, args.start_time.split(':'))
        end_hour, end_minute = map(int, args.end_time.split(':'))
        
        # Validate time values
        if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
            logging.error("Invalid start time. Hours must be 0-23, minutes must be 0-59.")
            return
        if not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
            logging.error("Invalid end time. Hours must be 0-23, minutes must be 0-59.")
            return
    except ValueError:
        logging.error("Invalid time format. Use HH:MM in 24-hour format.")
        return
    
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
    last_time_check = 0
    is_active_time = False if args.time_range else True
    
    logging.info(f"PIR-triggered photo capture started.")
    logging.info(f"Using pin GPIO{args.pin} for motion detection")
    logging.info(f"Photos will be saved to: {os.path.abspath(args.output)}")
    logging.info(f"Maximum resolution photos (4056x3040)")
    logging.info(f"Burst mode: {args.burst} photos with {args.burst_delay}s delay")
    logging.info(f"Cooldown between triggers: {args.cooldown}s")
    logging.info(f"PIR sensor sampling rate: {args.sampling_rate}s")
    
    if args.time_range:
        logging.info(f"Time-based activation enabled: {start_hour:02d}:{start_minute:02d} to {end_hour:02d}:{end_minute:02d}")
        is_active_time = is_time_in_range(start_hour, start_minute, end_hour, end_minute)
        logging.info(f"Current time is {'within' if is_active_time else 'outside'} the active range")
    else:
        logging.info("Time-based activation disabled: active 24/7")
    
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
            current_time = time.time()
            
            # Check if we need to update the active time status (check every minute)
            if args.time_range and current_time - last_time_check >= 60:
                previous_state = is_active_time
                is_active_time = is_time_in_range(start_hour, start_minute, end_hour, end_minute)
                last_time_check = current_time
                
                # Log if the active state changed
                if is_active_time != previous_state:
                    if is_active_time:
                        logging.info("Entering active time range - PIR sensor is now active")
                    else:
                        logging.info("Exiting active time range - PIR sensor is now inactive")
            
            # Only process motion detection if in active time range or if time range is disabled
            if is_active_time:
                # Read current state
                current_state = pi.read(args.pin)
                
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