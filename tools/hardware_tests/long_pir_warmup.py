#!/usr/bin/env python3
"""PIR sensor test with extended warm-up period.

Some PIR sensors need a long warm-up period when first powered on.
This script provides an extended warm-up time before testing.
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
    """Main function for PIR sensor warm-up and test."""
    parser = argparse.ArgumentParser(description='PIR sensor test with extended warm-up')
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number (BCM mode)')
    parser.add_argument('--warmup', type=int, default=120, help='Warm-up time in seconds')
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

    # Initial state check
    initial_state = GPIO.input(args.pin)
    print(f"Initial sensor state: {initial_state}")
    
    # Warm-up period
    print(f"Starting warm-up period ({args.warmup} seconds)...")
    print("The PIR sensor requires time to calibrate to the room's ambient IR levels.")
    print("Please ensure no motion occurs in the sensor's field of view during this time.")
    
    # Display progress during warm-up
    for i in range(args.warmup):
        if i % 10 == 0:  # Show status every 10 seconds
            state = GPIO.input(args.pin)
            print(f"Warming up: {i}/{args.warmup}s - Current state: {state}")
        time.sleep(1)
    
    print("Warm-up complete!")
    print(f"Now testing PIR sensor for {args.duration} seconds")
    print("Move in front of the sensor to trigger it")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    print("Time\t\tValue\tChange")
    print("-" * 60)
    
    # Testing loop
    last_state = GPIO.input(args.pin)
    start_time = time.time()
    changes = 0
    
    try:
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
            
        print("-" * 60)
        print(f"Test complete. Detected {changes} state changes over {args.duration} seconds.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        GPIO.cleanup(args.pin)
        print("GPIO cleaned up")

if __name__ == "__main__":
    main() 