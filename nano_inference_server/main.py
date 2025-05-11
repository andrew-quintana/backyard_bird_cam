#!/usr/bin/env python3
"""
Main entry point for the Nano Inference Server.
Connects all components: directory monitoring, inference, storage, and web API.
"""
import os
import sys
import time
import logging
import argparse
import threading
import json
from pathlib import Path
import signal
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import modules from this package
from inference.model import ModelHandler
from monitoring.directory_monitor import DirectoryMonitor
from storage.result_storage import ResultStorage
from api.server import APIServer

# Optional cloudflared import
try:
    from cloudflared_setup import setup_cloudflared
    CLOUDFLARED_AVAILABLE = True
except ImportError:
    CLOUDFLARED_AVAILABLE = False
    logger.warning("cloudflared_setup module not available, remote access will be disabled")

# Default configuration file path
DEFAULT_CONFIG_PATH = os.path.join(parent_dir, "config.json")

# Global flag for shutdown
shutdown_requested = False


def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM for graceful shutdown"""
    global shutdown_requested
    logger.info(f"Received signal {sig}, shutting down...")
    shutdown_requested = True


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file"""
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        sys.exit(1)


def process_image(model, storage, image_path):
    """Process a single image with the model and store the results"""
    try:
        logger.info(f"Processing image: {image_path}")
        
        # Run inference
        start_time = time.time()
        detections = model.detect(image_path)
        processing_time = time.time() - start_time
        
        # Generate annotated image if birds were detected
        annotated_path = None
        if detections:
            logger.info(f"Found {len(detections)} detections")
            annotated_path = model.annotate_image(image_path, detections)
        else:
            logger.info("No birds detected")
        
        # Save the results
        metadata = {
            "source": "directory_monitor",
            "original_path": image_path
        }
        
        result = storage.save_result(
            image_path=image_path,
            detections=detections,
            annotated_path=annotated_path,
            metadata=metadata,
            processing_time=processing_time
        )
        
        logger.info(f"Processed and saved results for {image_path}")
        return result
    
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return None


def main():
    """Main function that sets up and runs the inference server"""
    parser = argparse.ArgumentParser(description="Jetson Nano Bird Detection Inference Server")
    
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH,
                       help="Path to configuration file")
    parser.add_argument("--input-dir", "-i", type=str,
                       help="Directory to monitor for new images")
    parser.add_argument("--output-dir", "-o", type=str,
                       help="Directory to store results")
    parser.add_argument("--model", "-m", type=str,
                       help="Path to the detection model")
    parser.add_argument("--model-type", "-t", choices=["mobilenet", "yolo"],
                       help="Type of detection model")
    parser.add_argument("--device", "-d", choices=["cuda", "cpu"],
                       help="Device to run inference on")
    parser.add_argument("--port", "-p", type=int, 
                       help="Port for the API server")
    parser.add_argument("--development", action="store_true",
                       help="Run in development mode (without CUDA) for testing")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.input_dir:
        config["input_dir"] = args.input_dir
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.model:
        config["model_path"] = args.model
    if args.model_type:
        config["model_type"] = args.model_type
    if args.device:
        config["device"] = args.device
    if args.port:
        config["port"] = args.port
    
    # Force CPU in development mode
    if args.development:
        logger.info("Running in development mode - using CPU for inference")
        config["device"] = "cpu"
    
    # Set up components
    try:
        # Initialize model
        logger.info(f"Loading model from {config['model_path']}")
        model = ModelHandler(
            model_path=config["model_path"],
            confidence_threshold=config.get("confidence_threshold", 0.5),
            model_type=config["model_type"],
            device=config["device"],
            development_mode=args.development
        )
        
        # Initialize storage
        logger.info(f"Initializing storage in {config['output_dir']}")
        storage = ResultStorage(
            base_dir=config["output_dir"],
            max_results=config.get("max_results", 1000),
            organize_by_date=config.get("organize_by_date", True)
        )
        
        # Initialize directory monitor
        logger.info(f"Setting up directory monitor for {config['input_dir']}")
        monitor = DirectoryMonitor(
            input_dir=config["input_dir"],
            storage=storage,
            model=model,
            file_patterns=config.get("file_patterns", [".*\.(jpg|jpeg|png)$"])
        )
        
        # Initialize API server (if enabled)
        if not args.no_server:
            logger.info("Setting up API server")
            server = APIServer(
                storage=storage,
                model=model,
                config=config
            )
        
        # Setup cloudflared if enabled
        cloudflared_process = None
        if CLOUDFLARED_AVAILABLE and config.get("cloudflared", {}).get("enabled", False):
            logger.info("Setting up Cloudflare Tunnel for remote access")
            cloudflared_process = setup_cloudflared(
                tunnel_token=config.get("cloudflared", {}).get("tunnel_token"),
                port=config.get("port", 5000)
            )
        
        # Start the directory monitor
        logger.info("Starting directory monitor")
        monitor.start()
        
        # Start the API server in a separate thread (if enabled)
        if not args.no_server:
            logger.info(f"Starting API server on port {config['port']}")
            server_thread = threading.Thread(
                target=server.run,
                kwargs={"host": config.get("host", "0.0.0.0"), 
                        "port": config["port"],
                        "use_reloader": False}  # Disable reloader in thread
            )
            server_thread.daemon = True
            server_thread.start()
        
        # Main loop
        logger.info("Nano Inference Server is running. Press Ctrl+C to exit.")
        try:
            while not shutdown_requested:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        # Shutdown
        logger.info("Shutting down...")
        monitor.stop()
        logger.info("Shutdown complete")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 