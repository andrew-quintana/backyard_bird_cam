#!/usr/bin/env python3
"""Test script to check Picamera2 installation and functionality with high resolution."""

import sys
import time
import os

print("Python version:", sys.version)
print("Testing Picamera2 import...")

try:
    from picamera2 import Picamera2
    print("SUCCESS: Picamera2 imported successfully")
    
    # Try to initialize the camera
    try:
        camera = Picamera2()
        print("SUCCESS: Camera initialized")
        
        # Get the camera info
        camera_info = camera.camera_properties
        print(f"Camera Info: {camera_info}")
        
        # Create a configuration with high resolution
        try:
            # Use high resolution (default 4608x2592 for IMX708 camera module)
            # But reduce buffer count to help with memory constraints
            config = camera.create_still_configuration(
                buffer_count=2
            )
            print(f"SUCCESS: Created camera configuration with resolution: {config['main']['size']}")
            
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
                    
                    # Make sure the output directory exists
                    output_dir = "/home/fizz/projects/backyard_bird_cam/photos"
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = f"{output_dir}/highres_test_{int(time.time())}.jpg"
                    
                    # Try to capture an image
                    try:
                        print(f"Capturing high-resolution image to {output_path}...")
                        camera.capture_file(output_path)
                        print(f"SUCCESS: Captured high-resolution image to {output_path}")
                        print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
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
print("NOTE: A reboot is required for GPU memory changes to take effect.") 