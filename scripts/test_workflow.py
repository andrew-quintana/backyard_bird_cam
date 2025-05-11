#!/usr/bin/env python3

import time
import pigpio
import sys
import subprocess
import os

def check_pigpiod_running():
    """Check if pigpiod is running and return its PID."""
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error checking pigpiod: {e}")
        return None

def start_pigpiod():
    """Start pigpiod if not running."""
    if not check_pigpiod_running():
        print("Starting pigpiod...")
        try:
            subprocess.run(['sudo', 'pigpiod', '-v'], check=True)
            print("Waiting for pigpiod to initialize...")
            time.sleep(5)  # Give it time to fully start
        except Exception as e:
            print(f"Error starting pigpiod: {e}")
            return False
    return True

def test_pigpiod_connection(max_retries=5, delay=2):
    """Test connection to pigpiod with retries."""
    # First ensure pigpiod is running
    if not start_pigpiod():
        return False

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} to connect to pigpiod...")
            pi = pigpio.pi()
            if pi.connected:
                print("Successfully connected to pigpiod!")
                pi.stop()
                return True
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
        sys.exit(1) 