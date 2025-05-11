#!/usr/bin/env python3
"""
Modified server script for Jetson Nano with architecture compatibility.
This file provides a safe entry point that handles ARM-specific issues.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('jetson_server')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Jetson Nano Inference Server')
    parser.add_argument('--dev-mode', action='store_true', help='Run in development mode with mock data')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to listen on')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--model', type=str, help='Path to Keras model file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()

def setup_environment(args):
    """Set up environment variables and paths"""
    # Add the parent directory to the path so we can import modules
    current_dir = Path(__file__).resolve().parent
    if current_dir not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set up environment variables
    if args.verbose:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  # Verbose TF logging
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF verbosity
    
    logger.info(f"Command line arguments: {args}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")

def main():
    """Main entry point for the Jetson inference server"""
    args = parse_args()
    setup_environment(args)
    
    try:
        # Import the compatibility layer to handle architecture issues
        import jetson_compatibility
        jetson_compatibility.initialize_dev_mode()
        
        # Import Flask components for the web API
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        # Create the Flask application
        app = Flask(__name__)
        CORS(app)
        
        # Set up inference engine
        if args.dev_mode:
            logger.info("Running in development mode with mock inference")
            inference_engine = jetson_compatibility.get_mock_inference_engine()
        else:
            # Try to import TensorFlow safely
            tf = jetson_compatibility.safe_import_tensorflow()
            
            if tf is None:
                logger.warning("TensorFlow unavailable, falling back to mock inference")
                inference_engine = jetson_compatibility.get_mock_inference_engine()
            else:
                try:
                    # Find the original main.py to import its components
                    sys.path.insert(0, str(Path(__file__).resolve().parent))
                    from inference.inference_engine import InferenceEngine
                    
                    model_path = args.model
                    if not model_path:
                        # Look for model in common locations
                        for path in [
                            "./common/models/bird_mobilenet_v5data.keras",
                            "../common/models/bird_mobilenet_v5data.keras",
                            os.path.expanduser("~/projects/backyard_bird_cam/common/models/bird_mobilenet_v5data.keras")
                        ]:
                            if os.path.exists(path):
                                model_path = path
                                break
                    
                    if not model_path or not os.path.exists(model_path):
                        logger.warning("No model file found, falling back to mock inference")
                        inference_engine = jetson_compatibility.get_mock_inference_engine()
                    else:
                        logger.info(f"Loading model from: {model_path}")
                        inference_engine = InferenceEngine(model_path)
                        
                except Exception as e:
                    logger.error(f"Error setting up real inference engine: {e}")
                    logger.info("Falling back to mock inference engine")
                    inference_engine = jetson_compatibility.get_mock_inference_engine()
        
        # Define API routes
        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "mode": "development" if args.dev_mode else "production"})
        
        @app.route('/detect', methods=['POST'])
        def detect_birds():
            # This is a placeholder - in the real implementation,
            # we would process the uploaded image and run inference
            if 'image' not in request.files:
                return jsonify({"error": "No image provided"}), 400
                
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"error": "Empty image file"}), 400
                
            try:
                # Import image processing on-demand to avoid import errors
                from PIL import Image
                import numpy as np
                
                # Process the image
                img = Image.open(image_file.stream)
                
                # Run inference
                result = inference_engine.predict(img)
                
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error in bird detection: {e}")
                return jsonify({"error": str(e)}), 500
        
        # Start the server
        logger.info(f"Starting server on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=args.dev_mode)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 