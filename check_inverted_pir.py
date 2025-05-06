#!/usr/bin/env python3
"""Inverted PIR sensor test.

Some PIR sensors have an inverted signal where HIGH means no motion
and LOW means motion was detected. This script tests for that.
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
    """Main function for inverted PIR sensor test."""
    parser = argparse.ArgumentParser(description='Inverted PIR sensor test')
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number (BCM mode)')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--interval', type=float, default=0.2, help='Sampling interval in seconds')
    parser.add_argument('--pullup', action='store_true', help='Use pull-up resistor instead of pull-down')
    args = parser.parse_args()

    # Setup GPIO
    print(f"Setting up GPIO pin {args.pin} (BCM mode)")
    GPIO.setmode(GPIO.BCM)
    
    if args.pullup:
        print("Using pull-up resistor (inverted logic)")
        GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:
        print("Using pull-down resistor (normal logic)")
        GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    try:
        print(f"Testing PIR sensor on GPIO pin {args.pin} for {args.duration} seconds")
        print("Move in front of the sensor to trigger it")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        print("Time\t\tRaw Value\tInterpreted\tChange")
        print("-" * 60)
        
        # Initial state
        last_state = GPIO.input(args.pin)
        start_time = time.time()
        changes = 0
        
        # Testing loop
        while time.time() - start_time < args.duration:
            raw_state = GPIO.input(args.pin)
            
            # Interpret the state based on whether we're using inverted logic
            if args.pullup:
                interpreted_state = "No Motion" if raw_state else "MOTION!"
            else:
                interpreted_state = "MOTION!" if raw_state else "No Motion"
            
            # Check for state change
            change_marker = "  "
            if raw_state != last_state:
                change_marker = "* "
                changes += 1
                
            # Print current state
            elapsed = time.time() - start_time
            print(f"{elapsed:.1f}s\t\t{raw_state}\t\t{interpreted_state}\t{change_marker}")
            
            last_state = raw_state
            time.sleep(args.interval)
            
        print("-" * 60)
        print(f"Test complete. Detected {changes} state changes over {args.duration} seconds.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        GPIO.cleanup(args.pin)
        print("GPIO cleaned up")

if __name__ == "__main__":
    main() 