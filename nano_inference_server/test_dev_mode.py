#!/usr/bin/env python3
"""
Development testing script for the Nano Inference Server.

This script sets up a development environment with:
1. Mock image generation
2. Development mode for the model (no CUDA required)
3. Sample data for testing

Usage:
    python test_dev_mode.py

This will start a complete testing environment without requiring a Jetson Nano.
"""
import os
import sys
import time
import argparse
import logging
import shutil
import random
from pathlib import Path
import threading
import subprocess
from datetime import datetime, timedelta
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from inference.model import ModelHandler
from monitoring.directory_monitor import DirectoryMonitor
from storage.result_storage import ResultStorage

# Default paths
DATA_DIR = os.path.join(current_dir, "dev_data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
MODELS_DIR = os.path.join(DATA_DIR, "models")

# Bird colors for mock image generation
BIRD_COLORS = {
    "Northern Cardinal": (0, 0, 255),  # Red
    "American Robin": (0, 69, 255),    # Orange
    "Blue Jay": (255, 0, 0),           # Blue
    "House Sparrow": (139, 69, 19),    # Brown
    "American Goldfinch": (0, 215, 255), # Yellow
    "Chickadee": (128, 128, 128),      # Gray
    "Mourning Dove": (211, 211, 211),  # Light gray
    "House Finch": (0, 0, 128),        # Dark red
    "Red-winged Blackbird": (0, 0, 0), # Black with red spot
    "Downy Woodpecker": (0, 0, 0),     # Black and white
    "European Starling": (0, 0, 0),    # Black
    "Common Grackle": (0, 0, 0)        # Black
}

def setup_directories():
    """Create necessary directories for development testing"""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    logger.info(f"Created development directories in {DATA_DIR}")

def create_dummy_model():
    """Create a dummy model file for testing"""
    dummy_model_path = os.path.join(MODELS_DIR, "bird_model.pb")
    
    # Only create if it doesn't exist
    if not os.path.exists(dummy_model_path):
        # Create a dummy model file (just a placeholder)
        with open(dummy_model_path, "wb") as f:
            f.write(b"DUMMY_MODEL")
        
        # Create a classes file
        classes_path = os.path.join(MODELS_DIR, "classes.txt")
        with open(classes_path, "w") as f:
            f.write("Background\nBird\nOther")
    
    return dummy_model_path

def generate_mock_bird_image(output_path, species=None):
    """Generate a mock bird image for testing"""
    # Random image size between 640x480 and 1920x1080
    width = random.randint(640, 1920)
    height = random.randint(480, 1080)
    
    # Create a base image (sky background)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = (135, 206, 235)  # Sky blue
    
    # Add some green at the bottom (grass/trees)
    grass_height = random.randint(int(height * 0.2), int(height * 0.4))
    img[height - grass_height:, :] = (34, 139, 34)  # Forest green
    
    # Choose a random bird species if none specified
    if species is None:
        species = random.choice(list(BIRD_COLORS.keys()))
    
    # Get color for the species
    color = BIRD_COLORS.get(species, (255, 0, 255))  # Default to magenta if species not found
    
    # Draw a simple bird shape
    bird_size = random.randint(int(min(width, height) * 0.1), int(min(width, height) * 0.3))
    bird_x = random.randint(bird_size, width - bird_size)
    bird_y = random.randint(bird_size, height - grass_height - bird_size)
    
    # Draw bird body (circle)
    cv2.circle(img, (bird_x, bird_y), bird_size // 2, color, -1)
    
    # Draw bird head
    head_size = bird_size // 3
    head_angle = random.uniform(0, 2 * np.pi)
    head_x = int(bird_x + np.cos(head_angle) * bird_size // 2)
    head_y = int(bird_y + np.sin(head_angle) * bird_size // 2)
    cv2.circle(img, (head_x, head_y), head_size, color, -1)
    
    # Draw bird wing
    wing_angle = random.uniform(0, 2 * np.pi)
    wing_x = int(bird_x + np.cos(wing_angle) * bird_size // 2)
    wing_y = int(bird_y + np.sin(wing_angle) * bird_size // 2)
    cv2.ellipse(img, (wing_x, wing_y), (bird_size // 3, bird_size // 4), 
                random.randint(0, 180), 0, 180, color, -1)
    
    # Add some noise/texture
    noise = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.randn(noise, 0, 25)  # Add random noise
    img = cv2.add(img, noise)
    
    # Add timestamp and species name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(img, timestamp, (10, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, species, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Save the image
    cv2.imwrite(output_path, img)
    logger.debug(f"Generated mock bird image: {output_path}")
    
    return output_path

def generate_mock_images(num_images=5, interval=None):
    """Generate mock bird images in the input directory"""
    logger.info(f"Generating {num_images} mock bird images...")
    
    # Clear the input directory first
    for f in os.listdir(INPUT_DIR):
        os.remove(os.path.join(INPUT_DIR, f))
    
    if interval is None:
        # Generate all images at once
        for i in range(num_images):
            # Random bird species
            species = random.choice(list(BIRD_COLORS.keys()))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bird_{timestamp}_{i}.jpg"
            output_path = os.path.join(INPUT_DIR, filename)
            
            generate_mock_bird_image(output_path, species)
        
        logger.info(f"Generated {num_images} mock bird images in {INPUT_DIR}")
    else:
        # Generate images at intervals
        def generate_images_with_interval():
            for i in range(num_images):
                # Random bird species
                species = random.choice(list(BIRD_COLORS.keys()))
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bird_{timestamp}_{i}.jpg"
                output_path = os.path.join(INPUT_DIR, filename)
                
                generate_mock_bird_image(output_path, species)
                logger.info(f"Generated image {i+1}/{num_images}")
                
                if i < num_images - 1:
                    time.sleep(interval)
        
        # Start generation in a separate thread
        thread = threading.Thread(target=generate_images_with_interval)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Generating {num_images} mock bird images at {interval}s intervals...")

def run_inference_server():
    """Run the inference server in development mode"""
    # Run the main script with development mode flag
    cmd = [
        sys.executable,
        os.path.join(current_dir, "main.py"),
        "--development",
        "--input-dir", INPUT_DIR,
        "--output-dir", OUTPUT_DIR,
        "--model", os.path.join(MODELS_DIR, "bird_model.pb"),
        "--model-type", "mobilenet"
    ]
    
    logger.info("Starting inference server in development mode...")
    subprocess.run(cmd)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test environment for Nano Inference Server")
    parser.add_argument("--num-images", "-n", type=int, default=10,
                       help="Number of mock images to generate")
    parser.add_argument("--interval", "-i", type=float, default=None,
                       help="Interval in seconds between image generation (default: all at once)")
    parser.add_argument("--continuous", "-c", action="store_true",
                       help="Continuously generate images every few seconds")
    parser.add_argument("--no-server", action="store_true",
                       help="Don't start the inference server")
    
    args = parser.parse_args()
    
    # Setup development environment
    setup_directories()
    create_dummy_model()
    
    # Generate mock images
    if args.continuous:
        # Generate a few images to start
        generate_mock_images(5)
        
        # Start a thread to generate images continuously
        def continuous_generation():
            while True:
                # Wait a random time between 5-30 seconds
                wait_time = random.randint(5, 30)
                logger.info(f"Next bird in {wait_time} seconds...")
                time.sleep(wait_time)
                
                # Generate a single image
                generate_mock_images(1)
        
        thread = threading.Thread(target=continuous_generation)
        thread.daemon = True
        thread.start()
    else:
        # Generate the specified number of images
        generate_mock_images(args.num_images, args.interval)
    
    # Run the inference server if not disabled
    if not args.no_server:
        run_inference_server()
    else:
        logger.info("Server not started (--no-server flag provided)")
        
        # Keep the script running if continuous generation is enabled
        if args.continuous:
            logger.info("Continuous image generation is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopped.")

if __name__ == "__main__":
    main() 