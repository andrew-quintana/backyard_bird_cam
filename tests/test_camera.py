#!/usr/bin/env python3
"""
Test script for camera functionality.
This script takes a single test photo using picamera2 to verify the camera is working.
"""
from picamera2 import Picamera2
import time
import os

def main():
    print('Initializing camera...')
    
    # Initialize the camera with the Picamera2 library
    picam = Picamera2()
    config = picam.create_still_configuration()
    picam.configure(config)
    
    print('Starting camera...')
    picam.start()
    time.sleep(2)  # Warm-up time
    
    # Create unique filename with timestamp
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    filename = f'test_photo_{timestamp}.jpg'
    
    print(f'Taking test photo: {filename}...')
    picam.capture_file(filename)
    
    # Show the full path where the photo was saved
    full_path = os.path.abspath(filename)
    print(f'Photo saved to {full_path}')
    
    # Release camera resources
    picam.close()
    print('Camera test completed successfully')
    
if __name__ == "__main__":
    main() 