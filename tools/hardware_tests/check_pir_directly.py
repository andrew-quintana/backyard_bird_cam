#!/usr/bin/env python3
"""Simple PIR sensor GPIO test.

This script directly tests the PIR sensor's GPIO pin for troubleshooting.
"""
import sys
import time
import argparse

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: RPi.GPIO module not found. This script must run on a Raspberry Pi.")
    sys.exit(1)

def main():
    """Main function for simple PIR GPIO test."""
    parser = argparse.ArgumentParser(description='Simple PIR sensor GPIO test')
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number (BCM mode)')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--interval', type=float, default=0.2, help='Sampling interval in seconds')
    args = parser.parse_args()

    # Setup GPIO
    print(f"Setting up GPIO pin {args.pin} (BCM mode)")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    try:
        print(f"Testing PIR sensor on GPIO pin {args.pin} for {args.duration} seconds")
        print("Move in front of the sensor to trigger it")
        print("Press Ctrl+C to stop")
        print("-" * 40)
        print("Time\t\tValue\tChange")
        print("-" * 40)
        
        # Initial state
        last_state = GPIO.input(args.pin)
        start_time = time.time()
        changes = 0
        
        # Testing loop
        while time.time() - start_time < args.duration:
            current_state = GPIO.input(args.pin)
            
            # Check for state change
            change_marker = "  "
            if current_state != last_state:
                change_marker = "* "
                changes += 1
                
            # Print current state
            elapsed = time.time() - start_time
            print(f"{elapsed:.1f}s\t\t{current_state}\t{change_marker}")
            
            last_state = current_state
            time.sleep(args.interval)
            
        print("-" * 40)
        print(f"Test complete. Detected {changes} state changes over {args.duration} seconds.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        GPIO.cleanup(args.pin)
        print("GPIO cleaned up")

if __name__ == "__main__":
    main() 