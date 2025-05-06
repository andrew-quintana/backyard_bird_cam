#!/usr/bin/env python3
"""Test script to check Picamera2 installation and functionality with lower resolution."""

import sys
import time

print("Python version:", sys.version)
print("Testing Picamera2 import...")

try:
    from picamera2 import Picamera2
    print("SUCCESS: Picamera2 imported successfully")
    
    # Try to initialize the camera
    try:
        camera = Picamera2()
        print("SUCCESS: Camera initialized")
        
        # Create a configuration with lower resolution
        try:
            # Use a much lower resolution to reduce memory requirements
            config = camera.create_still_configuration(
                main={"size": (1280, 720)},  # 720p instead of 4K
                buffer_count=2  # Reduce buffer count
            )
            print("SUCCESS: Created camera configuration with lower resolution")
            
            # Configure the camera
            try:
                camera.configure(config)
                print("SUCCESS: Camera configured")
                
                # Try to start the camera
                try:
                    camera.start()
                    print("SUCCESS: Camera started")
                    
                    # Wait a moment for the camera to initialize
                    time.sleep(2)
                    
                    # Try to capture an image
                    try:
                        camera.capture_file("/tmp/test_capture_lowres.jpg")
                        print("SUCCESS: Captured test image to /tmp/test_capture_lowres.jpg")
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
    
print("\nTest complete.") 