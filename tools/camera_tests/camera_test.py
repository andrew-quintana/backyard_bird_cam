#!/usr/bin/env python3
"""Test script to check Picamera2 installation and functionality."""

import sys

print("Python version:", sys.version)
print("Testing Picamera2 import...")

try:
    from picamera2 import Picamera2
    print("SUCCESS: Picamera2 imported successfully")
    
    # Try to initialize the camera
    try:
        camera = Picamera2()
        print("SUCCESS: Camera initialized")
        
        # Create a simple configuration
        try:
            config = camera.create_still_configuration()
            print("SUCCESS: Created camera configuration")
            
            # Configure the camera
            try:
                camera.configure(config)
                print("SUCCESS: Camera configured")
                
                # Try to start the camera
                try:
                    camera.start()
                    print("SUCCESS: Camera started")
                    
                    # Try to capture an image
                    try:
                        camera.capture_file("/tmp/test_capture.jpg")
                        print("SUCCESS: Captured test image to /tmp/test_capture.jpg")
                    except Exception as e:
                        print(f"ERROR: Failed to capture image: {e}")
                    
                    # Stop the camera
                    camera.stop()
                    camera.close()
                    print("Camera stopped and resources released")
                    
                except Exception as e:
                    print(f"ERROR: Failed to start camera: {e}")
            except Exception as e:
                print(f"ERROR: Failed to configure camera: {e}")
        except Exception as e:
            print(f"ERROR: Failed to create camera configuration: {e}")
    except Exception as e:
        print(f"ERROR: Failed to initialize camera: {e}")
        
except ImportError as e:
    print(f"ERROR: Failed to import Picamera2: {e}")
    print("\nPicamera2 installation instructions:")
    print("1. Ensure camera is enabled in raspi-config")
    print("2. Install libcamera and picamera2 packages:")
    print("   sudo apt update")
    print("   sudo apt install -y python3-libcamera python3-picamera2")
    
print("\nTest complete.") 