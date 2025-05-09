#!/usr/bin/env python3
"""
Debug script for the PIR sensor.
This simply displays the current state of the PIR sensor in real-time.
"""
import pigpio
import time
import os
import signal
import sys
import datetime

# Default GPIO pin
PIN = 4

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit cleanly"""
    print("\nMonitoring stopped.")
    sys.exit(0)

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)

def main():
    # Get pin from environment or command line
    if len(sys.argv) > 1:
        pin = int(sys.argv[1])
    else:
        pin = PIN

    print(f"PIR Sensor Debug - Using GPIO pin {pin}")
    print("---------------------------------------------")
    print("This will continuously display the sensor state.")
    print("Press Ctrl+C to exit\n")
    
    # Connect to pigpio daemon
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon!")
        print("Try running: sudo systemctl start pigpiod")
        return
    
    # Set up the pin
    pi.set_mode(pin, pigpio.INPUT)
    
    # Initial state
    last_state = pi.read(pin)
    last_change = time.time()
    
    try:
        while True:
            # Get current state and timestamp
            current_state = pi.read(pin)
            current_time = time.time()
            
            # Format timestamp
            timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Display state with clear indication
            state_str = "HIGH (1)" if current_state == 1 else "LOW (0) "
            
            # Add indication for change
            if current_state != last_state:
                change_time = current_time - last_change
                print(f"[{timestamp}] State CHANGED to {state_str} (after {change_time:.3f}s)")
                last_state = current_state
                last_change = current_time
            else:
                # Only print every second to avoid flooding the terminal
                if int(current_time) % 1 == 0:
                    print(f"[{timestamp}] Current state: {state_str}")
            
            # Small delay
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        if pi.connected:
            pi.stop()
        print("Monitoring ended.")

if __name__ == "__main__":
    main() 