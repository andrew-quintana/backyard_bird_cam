#!/usr/bin/env python3
"""Script to directly set the camera lens position."""
import sys
import os
import argparse
import logging
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pi_bird_cam.camera.camera_handler import CameraHandler

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to set lens position."""
    parser = argparse.ArgumentParser(description='Set camera lens position directly')
    parser.add_argument('position', type=float, help='Lens position value (0.0-15.0). 0 is infinity, 15 is closest.')
    parser.add_argument('--test', action='store_true', help='Take a test photo after setting lens position')
    parser.add_argument('--output', default='test_photo.jpg', help='Output path for test photo (default: test_photo.jpg)')
    args = parser.parse_args()

    # Validate position
    if not 0 <= args.position <= 15:
        print("Error: Lens position must be between 0.0 and 15.0")
        sys.exit(1)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize camera with custom lens position
        logger.info(f"Initializing camera with lens position: {args.position}")
        
        # Create camera handler with default settings
        camera = CameraHandler(
            resolution=(4056, 3040),
            rotation=0,
            focus_distance_inches=8  # This will be overridden
        )
        
        # Override the lens position directly
        camera.camera.camera_controls["LensPosition"] = args.position
        logger.info(f"Lens position set to: {args.position}")
        
        # Take a test photo if requested
        if args.test:
            logger.info(f"Taking test photo with lens position {args.position}")
            output_path = os.path.abspath(args.output)
            camera.take_photo(output_path)
            logger.info(f"Test photo saved to: {output_path}")
        
        # Clean up
        camera.cleanup()
        logger.info("Camera resources cleaned up")
        
    except Exception as e:
        logger.error(f"Error setting lens position: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 