#!/usr/bin/env python3
"""
Log PIR sensor activity to a file for a specified duration.
This will run for a set time and record all state changes.
"""
import pigpio
import time
import os
import datetime
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Log PIR sensor activity for a specific duration')
    parser.add_argument('--pin', type=int, default=4, help='GPIO pin number (default: 4)')
    parser.add_argument('--time', type=int, default=60, help='Duration in seconds (default: 60)')
    parser.add_argument('--output', type=str, default='pir_activity.log', help='Output log file (default: pir_activity.log)')
    args = parser.parse_args()
    
    # Get parameters
    PIR_PIN = args.pin
    DURATION = args.time
    LOG_FILE = args.output
    
    print(f"PIR Activity Logger")
    print(f"Using GPIO pin: {PIR_PIN}")
    print(f"Duration: {DURATION} seconds")
    print(f"Log file: {LOG_FILE}")
    print("Starting...")
    
    # Connect to pigpio daemon
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon!")
        print("Try running: sudo systemctl start pigpiod")
        return
    
    # Set up the pin
    pi.set_mode(PIR_PIN, pigpio.INPUT)
    
    # Initial state
    last_state = pi.read(PIR_PIN)
    
    # Open log file
    with open(LOG_FILE, 'w') as log:
        # Write header
        log.write(f"PIR Activity Log - Pin {PIR_PIN}\n")
        log.write(f"Started at: {datetime.datetime.now()}\n")
        log.write(f"Initial state: {'HIGH (1)' if last_state == 1 else 'LOW (0)'}\n")
        log.write("-" * 50 + "\n")
        
        # Record start time
        start_time = time.time()
        end_time = start_time + DURATION
        changes = 0
        last_change_time = start_time
        
        # Monitor until duration is reached
        while time.time() < end_time:
            # Read current state
            current_state = pi.read(PIR_PIN)
            
            # If state changed
            if current_state != last_state:
                changes += 1
                now = time.time()
                elapsed = now - start_time
                since_last = now - last_change_time
                timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                # Build log message
                if current_state == 1:
                    message = f"[{timestamp}] Motion DETECTED! (Change #{changes}, after {since_last:.3f}s)"
                else:
                    message = f"[{timestamp}] Motion ENDED (Change #{changes}, after {since_last:.3f}s)"
                
                # Write to log and console
                log.write(message + "\n")
                log.flush()  # Ensure it's written immediately
                print(message)
                
                # Update state and time
                last_state = current_state
                last_change_time = now
            
            # Small delay to prevent CPU hogging
            time.sleep(0.01)  # Smaller delay for more precise timing
            
        # Log summary
        remaining = int(DURATION - (time.time() - start_time))
        if remaining > 0:
            time.sleep(remaining)  # Wait for exactly the specified duration
            
        end_message = f"\nLogging completed at {datetime.datetime.now()}"
        summary = f"Total changes detected: {changes} in {DURATION} seconds"
        log.write(end_message + "\n")
        log.write(summary + "\n")
        print(end_message)
        print(summary)
    
    # Clean up
    if pi.connected:
        pi.stop()
    
    print(f"Log file written to: {LOG_FILE}")

if __name__ == "__main__":
    main() 