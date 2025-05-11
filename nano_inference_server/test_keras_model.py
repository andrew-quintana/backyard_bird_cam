#!/usr/bin/env python3
"""
Testing script for using a Keras model with the Nano Inference Server.

This script allows testing with an actual .keras model file from ./common/models/
instead of the mock development mode.

Usage:
    python test_keras_model.py --model-path ./common/models/your_model.keras
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
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
from storage.result_storage import ResultStorage
from test_dev_mode import generate_mock_bird_image, DATA_DIR, INPUT_DIR, OUTPUT_DIR

def verify_keras_model(model_path):
    """Verify that the Keras model exists and can be loaded"""
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return False
        
    if not model_path.endswith('.keras'):
        logger.warning(f"Model file {model_path} doesn't have .keras extension. It may not be a Keras model.")
    
    try:
        # Try importing TensorFlow
        import tensorflow as tf
        logger.info("TensorFlow is available.")
        
        # Check TensorFlow version
        logger.info(f"TensorFlow version: {tf.__version__}")
        
        return True
    except ImportError:
        logger.error("TensorFlow is not installed. Cannot load Keras models.")
        logger.info("Install TensorFlow with: pip install tensorflow")
        return False

def test_with_keras_model(model_path, num_images=3):
    """Test the inference system with a Keras model"""
    # Ensure directories exist
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Verify the model
    if not verify_keras_model(model_path):
        return False
    
    # Create a storage instance
    storage = ResultStorage(base_dir=OUTPUT_DIR, organize_by_date=True)
    
    # Create model handler
    try:
        model = ModelHandler(
            model_path=model_path,
            model_type="keras",
            device="cpu",
            confidence_threshold=0.5,
            development_mode=False
        )
        logger.info("Successfully created model handler")
    except Exception as e:
        logger.error(f"Failed to create model handler: {str(e)}")
        return False
    
    # Generate test images
    logger.info(f"Generating {num_images} test images")
    test_images = []
    for i in range(num_images):
        # Generate a test image
        image_path = os.path.join(INPUT_DIR, f"test_keras_{i}.jpg")
        generate_mock_bird_image(image_path)
        test_images.append(image_path)
    
    # Run inference on each image
    for image_path in test_images:
        logger.info(f"Testing inference on {image_path}")
        
        # Run detection
        detections = model.detect(image_path)
        
        # Create annotated image if detections found
        if detections:
            logger.info(f"Found {len(detections)} detections")
            for i, detection in enumerate(detections):
                logger.info(f"  Detection {i+1}: {detection['class_name']} ({detection['confidence']:.2f})")
                if 'species' in detection:
                    logger.info(f"    Species: {detection['species']} ({detection.get('species_confidence', 0):.2f})")
            
            annotated_path = model.annotate_image(image_path, detections)
            logger.info(f"Created annotated image: {annotated_path}")
        else:
            logger.info("No detections found")
    
    logger.info("Keras model testing completed successfully")
    return True

def run_inference_server_with_keras(model_path):
    """Run the inference server with the Keras model"""
    # Import main module
    from main import load_config, DEFAULT_CONFIG_PATH
    
    # Load the default config
    config = load_config(DEFAULT_CONFIG_PATH)
    
    # Override with our settings
    config["model_path"] = model_path
    config["model_type"] = "keras"
    config["device"] = "cpu"
    config["input_dir"] = INPUT_DIR
    config["output_dir"] = OUTPUT_DIR
    
    # Update and save the config
    with open(os.path.join(current_dir, "keras_test_config.json"), "w") as f:
        import json
        json.dump(config, f, indent=4)
    
    # Run the main script with custom config
    cmd = [
        sys.executable,
        os.path.join(current_dir, "main.py"),
        "--config", os.path.join(current_dir, "keras_test_config.json")
    ]
    
    logger.info("Starting inference server with Keras model...")
    import subprocess
    subprocess.run(cmd)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Keras model with Nano Inference Server")
    parser.add_argument("--model-path", "-m", type=str, required=True,
                       help="Path to the .keras model file")
    parser.add_argument("--num-images", "-n", type=int, default=3,
                       help="Number of test images to generate")
    parser.add_argument("--test-only", "-t", action="store_true",
                       help="Only test the model without starting the server")
    
    args = parser.parse_args()
    
    # Absolute path for model
    model_path = os.path.abspath(args.model_path)
    logger.info(f"Using Keras model: {model_path}")
    
    # Test the model
    if test_with_keras_model(model_path, args.num_images):
        if not args.test_only:
            # Start the server with the Keras model
            run_inference_server_with_keras(model_path)
    else:
        logger.error("Keras model testing failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 