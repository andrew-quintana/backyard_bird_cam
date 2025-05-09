#!/usr/bin/env python3
"""
Test script for PIR motion sensor functionality using pigpio library.
This script monitors the PIR sensor and prints when motion is detected.
"""
import pigpio
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path('..') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

# Set the GPIO pin number where your PIR sensor is connected
PIR_PIN = int(os.getenv('PIR_PIN', 4))

def main():
    print("PIR Motion Sensor Test")
    print("=====================")
    print(f"Using GPIO pin: {PIR_PIN}")
    
    try:
        # Connect to the pigpio daemon
        pi = pigpio.pi()
        if not pi.connected:
            print("Failed to connect to pigpio daemon.")
            print("Please run: sudo pigpiod")
            return
        
        # Set pin mode
        pi.set_mode(PIR_PIN, pigpio.INPUT)
        
        print(f"Initial sensor state: {pi.read(PIR_PIN)}")
        print("Sensor warming up... (5 seconds)")
        print("This allows the sensor to stabilize")
        
        # Warmup time (reduced for testing)
        time.sleep(5)
        
        print("Ready to detect motion!")
        print("Press CTRL+C to exit")
        
        detection_count = 0
        last_state = pi.read(PIR_PIN)
        
        while True:
            # Read the current state
            current_state = pi.read(PIR_PIN)
            
            # Check if motion was detected (rising edge: 0->1)
            if current_state == 1 and last_state == 0:
                detection_count += 1
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] Motion detected! (Count: {detection_count})")
            
            # Update last state
            last_state = current_state
            
            # Small sleep to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nTest ended by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if 'pi' in locals() and pi.connected:
            pi.stop()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main() 