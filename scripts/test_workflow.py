#!/usr/bin/env python3

import time
import pigpio
import sys
import subprocess
import os
import socket

def check_port_available(port=8888):
    """Check if port is available and listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False

def check_pigpiod_running():
    """Check if pigpiod is running and return its PID."""
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
        if result.returncode == 0:
            pid = result.stdout.strip()
            print(f"Found pigpiod process with PID: {pid}")
            return pid
        print("No pigpiod process found")
        return None
    except Exception as e:
        print(f"Error checking pigpiod: {e}")
        return None

def start_pigpiod():
    """Start pigpiod if not running."""
    if not check_pigpiod_running():
        print("Starting pigpiod...")
        try:
            # Stop any existing instances first
            subprocess.run(['sudo', 'killall', 'pigpiod'], capture_output=True)
            time.sleep(1)
            
            # Start with verbose output
            result = subprocess.run(['sudo', 'pigpiod', '-v'], 
                                 capture_output=True, 
                                 text=True)
            print(f"Pigpiod start output: {result.stdout}")
            if result.stderr:
                print(f"Pigpiod start errors: {result.stderr}")
            
            print("Waiting for pigpiod to initialize...")
            time.sleep(10)  # Increased wait time
            
            # Verify port is listening
            if check_port_available():
                print("Port 8888 is now listening")
            else:
                print("Warning: Port 8888 is not listening")
                
        except Exception as e:
            print(f"Error starting pigpiod: {e}")
            return False
    return True

def test_pigpiod_connection(max_retries=5, delay=3):
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