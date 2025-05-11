#!/usr/bin/env python3

import time
import pigpio
import sys
import os
import subprocess

def check_pigpiod_running():
    """Check if pigpiod is running and return its PID."""
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error checking pigpiod: {e}")
        return None

def test_pigpiod_connection(max_retries=5, delay=2):
    """Test connection to pigpiod with retries."""
    # First check if pigpiod is running
    pid = check_pigpiod_running()
    if not pid:
        print("pigpiod is not running. Starting it...")
        try:
            subprocess.run(['sudo', 'pigpiod', '-v'], check=True)
            time.sleep(2)  # Give it time to start
        except Exception as e:
            print(f"Failed to start pigpiod: {e}")
            return False
    
    # Now try to connect
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} to connect to pigpiod...")
            print(f"Current PIGPIO_ADDR: {os.environ.get('PIGPIO_ADDR', 'not set')}")
            print(f"Current PIGPIO_PORT: {os.environ.get('PIGPIO_PORT', 'not set')}")
            
            # Try connecting with explicit parameters
            pi = pigpio.pi('localhost', 8888)
            if pi.connected:
                print("Successfully connected to pigpiod!")
                pi.stop()
                return True
            else:
                print("Connection failed - pi.connected is False")
        except Exception as e:
            print(f"Connection attempt failed: {e}")
        
        if attempt < max_retries - 1:
            print(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("Failed to connect to pigpiod after all attempts")
    return False

if __name__ == "__main__":
    print("Testing pigpiod connection...")
    if test_pigpiod_connection():
        print("\nPigpiod connection test passed!")
        print("\nNow you can try running the camera script:")
        print("python3 -u -m pi_bird_cam.main --debug")
    else:
        print("\nPigpiod connection test failed!")
        print("Please check if pigpiod is running: sudo pigpiod -v")
        print("You may need to:")
        print("1. Stop any existing pigpiod: sudo killall pigpiod")
        print("2. Start pigpiod fresh: sudo pigpiod -v")
        print("3. Wait a few seconds and try again")
        sys.exit(1) 