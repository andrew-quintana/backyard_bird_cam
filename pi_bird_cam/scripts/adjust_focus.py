#!/usr/bin/env python3
"""Script to adjust camera focus distance from command line."""
import sys
import os
import argparse
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to adjust focus distance."""
    parser = argparse.ArgumentParser(description='Adjust camera focus distance')
    parser.add_argument('distance', type=float, help='Focus distance in inches (8 inches to infinity)')
    args = parser.parse_args()

    # Validate distance
    if args.distance < 8:
        print("Error: Focus distance must be at least 8 inches")
        sys.exit(1)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Update settings
        settings = Settings()
        settings.set("camera", "focus_distance_inches", args.distance)
        logger.info(f"Focus distance updated to {args.distance} inches")
        
        # Print current settings
        current = settings.get("camera", "focus_distance_inches")
        logger.info(f"Current focus distance: {current} inches")
        
    except Exception as e:
        logger.error(f"Error updating focus distance: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 