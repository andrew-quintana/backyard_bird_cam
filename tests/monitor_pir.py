#!/usr/bin/env python3
"""
Simple script to monitor the PIR sensor state.
This gives continuous feedback on the sensor's state to help with troubleshooting.
"""
import pigpio
import time
import os
import signal
import sys

# Get the PIR pin from environment or use default
PIR_PIN = int(os.getenv('PIR_PIN', 4))

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit cleanly"""
    print("\nMonitoring stopped.")
    sys.exit(0)

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)

def main():
    print(f"PIR Sensor Monitor - Using GPIO pin {PIR_PIN}")
    print("---------------------------------------------")
    print("Press Ctrl+C to exit\n")
    
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
    print(f"Initial state: {'HIGH (1)' if last_state == 1 else 'LOW (0)'}")
    
    # Monitor changes
    changes = 0
    start_time = time.time()
    
    try:
        while True:
            # Read current state
            current_state = pi.read(PIR_PIN)
            
            # If state changed
            if current_state != last_state:
                changes += 1
                timestamp = time.strftime("%H:%M:%S")
                elapsed = time.time() - start_time
                
                if current_state == 1:
                    print(f"[{timestamp}] Motion DETECTED! (Change #{changes}, after {elapsed:.1f}s)")
                else:
                    print(f"[{timestamp}] Motion ENDED (Change #{changes}, after {elapsed:.1f}s)")
                
                # Reset timer
                start_time = time.time()
                
                # Update last state
                last_state = current_state
            
            # Small delay to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        # This will be caught by the signal handler
        pass
    finally:
        if pi.connected:
            pi.stop()

if __name__ == "__main__":
    main() 