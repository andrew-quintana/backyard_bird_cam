#!/usr/bin/env python3
"""PIR Sensor Calibration Tool.

This script helps calibrate the PIR sensor by continuously reading
and displaying the raw sensor values.
"""
import time
import logging
import argparse
import sys
import os
import signal

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: RPi.GPIO module not found. This script must run on a Raspberry Pi.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('pir_calibration')

# Flag to indicate if shutdown is requested
shutdown_requested = False

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    global shutdown_requested
    logger.info(f"Received signal {sig}, initiating shutdown...")
    shutdown_requested = True

def setup_gpio(pin):
    """Setup GPIO pin for PIR sensor."""
    logger.info(f"Setting up GPIO pin {pin} in BCM mode")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Print current pin state
    initial_state = GPIO.input(pin)
    logger.info(f"Initial state of GPIO pin {pin}: {initial_state}")
    
    return pin

def cleanup_gpio(pin):
    """Clean up GPIO resources."""
    GPIO.cleanup(pin)

def main():
    """Main function for PIR sensor calibration."""
    parser = argparse.ArgumentParser(description='PIR Sensor Calibration Tool')
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number (BCM mode) connected to the PIR sensor')
    parser.add_argument('--interval', type=float, default=0.1, help='Sampling interval in seconds')
    parser.add_argument('--duration', type=int, default=0, help='Duration in seconds (0 for continuous)')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--warmup', type=int, default=10, help='Warm-up time in seconds for the PIR sensor')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting PIR sensor calibration on GPIO pin {args.pin}")
    logger.info(f"Sampling interval: {args.interval} seconds")
    if args.duration > 0:
        logger.info(f"Duration: {args.duration} seconds")
    else:
        logger.info("Running continuously (press Ctrl+C to stop)")
    
    # Setup GPIO
    pin = setup_gpio(args.pin)
    
    # Warm-up period for PIR sensor if specified
    if args.warmup > 0:
        logger.info(f"Warming up PIR sensor for {args.warmup} seconds...")
        warmup_end = time.time() + args.warmup
        while time.time() < warmup_end and not shutdown_requested:
            # Log the pin state periodically during warmup
            value = GPIO.input(pin)
            logger.debug(f"PIR pin state during warmup: {value}")
            time.sleep(1)
        logger.info("Warm-up complete")
    
    # Print CSV header if in CSV mode
    if args.csv:
        print("timestamp,value")
    
    try:
        start_time = time.time()
        sample_count = 0
        last_value = None
        
        # Main loop
        while not shutdown_requested:
            # Check if duration has elapsed
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                break
                
            # Read sensor value
            value = GPIO.input(pin)
            timestamp = time.time()
            
            # Log value changes in debug mode
            if args.debug and value != last_value:
                logger.debug(f"PIR value changed from {last_value} to {value}")
                last_value = value
            
            # Output value
            if args.csv:
                print(f"{timestamp:.6f},{value}")
            else:
                print(f"[{time.strftime('%H:%M:%S', time.localtime(timestamp))}] PIR value: {value}")
            
            # Increment sample count
            sample_count += 1
            
            # Sleep for the specified interval
            time.sleep(args.interval)
            
        logger.info(f"Calibration complete. Collected {sample_count} samples over {time.time() - start_time:.2f} seconds.")
        
    except KeyboardInterrupt:
        logger.info("Calibration interrupted by user")
    finally:
        # Clean up resources
        cleanup_gpio(pin)
        logger.info("GPIO resources cleaned up")

if __name__ == "__main__":
    main() 