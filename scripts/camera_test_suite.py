#!/usr/bin/env python3
"""
Camera Test Suite

This script takes a series of test photos with different camera parameters
and overlays the settings onto each image to help determine optimal settings
for the bird camera.
"""

import os
import subprocess
import argparse
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Define the output directory
DEFAULT_OUTPUT_DIR = "data/test_photos"

# Camera parameters to test
TEST_PROFILES = {
    "standard": {
        "description": "Standard daylight shot",
        "params": "--ev 0 --awb auto --sharpness 1.0 --contrast 1.0 --brightness 0.0 --saturation 1.0"
    },
    "bright": {
        "description": "Brighter exposure for shadowy areas",
        "params": "--ev 1.0 --awb auto --sharpness 1.0 --contrast 1.0 --brightness 0.2 --saturation 1.0"
    },
    "darker": {
        "description": "Reduced exposure for bright conditions",
        "params": "--ev -0.5 --awb auto --sharpness 1.0 --contrast 1.0 --brightness 0.0 --saturation 1.0"
    },
    "vivid": {
        "description": "Vivid colors for better bird detail",
        "params": "--ev 0 --awb auto --sharpness 1.2 --contrast 1.2 --brightness 0.0 --saturation 1.3"
    },
    "high_detail": {
        "description": "High detail for feather textures",
        "params": "--ev 0 --awb auto --sharpness 1.5 --contrast 1.1 --brightness 0.0 --saturation 1.0"
    },
    "fast_shutter": {
        "description": "Fast shutter for bird movement (1/1000s)",
        "params": "--shutter 1000 --gain 2.0 --awb auto --sharpness 1.0"
    },
    "medium_shutter": {
        "description": "Medium shutter speed (1/250s)",
        "params": "--shutter 4000 --gain 1.5 --awb auto --sharpness 1.0"
    },
    "low_light": {
        "description": "Low light conditions",
        "params": "--shutter 20000 --gain 2.5 --awb tungsten --brightness 0.1"
    },
    "tungsten": {
        "description": "Indoor tungsten white balance",
        "params": "--ev 0 --awb tungsten --sharpness 1.0 --contrast 1.0"
    },
    "daylight": {
        "description": "Outdoor daylight white balance",
        "params": "--ev 0 --awb daylight --sharpness 1.0 --contrast 1.0"
    },
    "cloudy": {
        "description": "Cloudy day white balance",
        "params": "--ev 0 --awb cloudy --sharpness 1.0 --contrast 1.0"
    },
    "macro_mode": {
        "description": "Close-up shots with macro focus",
        "params": "--ev 0 --awb auto --autofocus-mode auto --autofocus-range macro"
    },
    "max_quality": {
        "description": "Maximum quality settings",
        "params": "--quality 100 --ev 0 --awb auto --sharpness 1.2 --contrast 1.1 --saturation 1.1"
    }
}

# Resolution presets
RESOLUTION_PRESETS = {
    "low": (640, 480),
    "medium": (1640, 1232),
    "high": (2028, 1520),
    "full": (4056, 3040)  # For HQ camera, adjust if using a different camera
}

def create_output_dir(output_dir):
    """Create the output directory if it doesn't exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

def add_text_overlay(image_path, text, output_path=None):
    """Add text overlay to image with parameters"""
    if output_path is None:
        output_path = image_path
    
    try:
        # Open the image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Try to use a standard font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial", 24)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text position (top right corner)
        wrapped_text = textwrap.fill(text, width=40)
        
        # Create semi-transparent background for text
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        margin = 10
        rect_top = margin
        rect_left = img.width - text_width - margin * 2
        
        # Draw semi-transparent background
        draw.rectangle(
            [(rect_left, rect_top), 
             (rect_left + text_width + margin * 2, rect_top + text_height + margin)],
            fill=(0, 0, 0, 128)
        )
        
        # Draw text
        draw.text(
            (rect_left + margin, rect_top + margin/2), 
            wrapped_text, 
            font=font, 
            fill=(255, 255, 255)
        )
        
        # Save the modified image
        img.save(output_path)
        print(f"Added overlay to {output_path}")
        
    except Exception as e:
        print(f"Error adding text overlay: {e}")

def capture_image(output_file, params, width=None, height=None):
    """Capture an image with the specified parameters"""
    command = ["libcamera-still", "-o", output_file, "-n"]
    
    # Add resolution if specified
    if width and height:
        command.extend(["--width", str(width), "--height", str(height)])
    
    # Add other parameters
    command.extend(params.split())
    
    # Execute the command
    try:
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"Error capturing image: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Camera Test Suite")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                       help=f"Output directory for test photos (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--resolution", "-r", default="medium",
                       choices=list(RESOLUTION_PRESETS.keys()),
                       help="Resolution preset to use (default: medium)")
    parser.add_argument("--profiles", "-p", nargs="+",
                       choices=list(TEST_PROFILES.keys()) + ["all"],
                       default=["all"],
                       help="Specific profiles to test (default: all)")
    
    args = parser.parse_args()
    
    # Determine which profiles to use
    profiles_to_test = TEST_PROFILES.keys() if "all" in args.profiles else args.profiles
    
    # Get resolution
    width, height = RESOLUTION_PRESETS[args.resolution]
    
    # Create output directory
    create_output_dir(args.output)
    
    # Start testing
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Starting camera tests at {timestamp}")
    print(f"Resolution: {width}x{height}")
    print(f"Output directory: {args.output}")
    
    # Take each test photo
    for profile_name in profiles_to_test:
        profile = TEST_PROFILES[profile_name]
        
        print(f"\nTesting profile: {profile_name}")
        print(f"Description: {profile['description']}")
        print(f"Parameters: {profile['params']}")
        
        # Create output filename
        output_file = os.path.join(args.output, f"{profile_name}_{timestamp}.jpg")
        
        # Capture the image
        success = capture_image(output_file, profile["params"], width, height)
        
        if success:
            # Add overlay with parameters
            overlay_text = f"{profile_name}\n{profile['description']}\n{profile['params']}\n{width}x{height}"
            add_text_overlay(output_file, overlay_text)
        
        # Small delay between captures
        time.sleep(1)
    
    print(f"\nAll tests completed. Photos saved to {args.output}")

if __name__ == "__main__":
    main() 