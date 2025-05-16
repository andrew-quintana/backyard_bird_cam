"""Main module for the Raspberry Pi Bird Camera project."""
import time
import logging
import os
import signal
import sys
from sensors.pir_sensor import PIRSensor
from camera.camera_handler import CameraHandler
from storage.photo_storage import PhotoStorage
from uploader.uploader import Uploader
from inference.inference_engine import InferenceEngine
from config.settings import Settings


# Flag to indicate if shutdown is requested
shutdown_requested = False


def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    global shutdown_requested
    logging.info(f"Received signal {sig}, initiating shutdown...")
    shutdown_requested = True
    # Don't exit immediately, let the main loop handle cleanup


def setup_logging(debug=False):
    """Setup logging configuration.
    
    Args:
        debug (bool): If True, sets log level to DEBUG for more detailed logs
    """
    # Get log level from environment or use default
    log_level = os.getenv('LOG_LEVEL', 'DEBUG' if debug else 'INFO')
    log_level = getattr(logging, log_level.upper())
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/bird_camera.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set logging level for specific components
    for component in ['sensors.pir_sensor', 'camera.camera_handler', 
                     'storage.photo_storage', 'uploader.uploader',
                     'inference.inference_engine']:
        logging.getLogger(component).setLevel(log_level)


def main():
    """Main function for the bird camera application."""
    # Check for debug mode flag
    debug_mode = "--debug" in sys.argv or os.getenv('DEBUG') == '1'
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    setup_logging(debug=debug_mode)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Bird Camera application")
    if debug_mode:
        logger.info("Running in DEBUG mode - detailed logs enabled")
    
    # Initialize components
    settings = Settings()
    
    # Create required directories
    os.makedirs(settings.get("storage", "base_dir"), exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize components with retry
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Initialize PIR sensor
            pir_sensor = PIRSensor(
                pin=settings.get("pir_sensor", "pin"),
                cooldown_time=settings.get("pir_sensor", "trigger_cooldown")
            )
            
            # Initialize camera
            camera = CameraHandler(
                resolution=tuple(settings.get("camera", "resolution")),
                rotation=settings.get("camera", "rotation"),
                focus_distance_inches=settings.get("camera", "focus_distance_inches")
            )
            
            # Initialize storage
            storage = PhotoStorage(
                base_dir=settings.get("storage", "base_dir"),
                max_photos=settings.get("storage", "max_photos")
            )
            
            # Break out of retry loop if successful
            break
            
        except Exception as e:
            logger.error(f"Error initializing components (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to initialize components after maximum retries")
                return 1
    
    # These components are optional for the basic functionality
    uploader = None
    inference = None
    
    # Only initialize uploader if auto_upload is enabled
    if settings.get("uploader", "auto_upload"):
        try:
            uploader = Uploader(
                service_type=settings.get("uploader", "service"),
                credentials=None  # TODO: Add credentials handling
            )
            logger.info("Uploader initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize uploader: {e}")
    
    # Only initialize inference if auto_classify is enabled
    if settings.get("inference", "auto_classify"):
        try:
            inference = InferenceEngine(
                model_path=settings.get("inference", "model_path"),
                confidence_threshold=settings.get("inference", "confidence_threshold")
            )
            logger.info("Inference engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize inference engine: {e}")
    
    try:
        logger.info("Entering main loop")
        
        # Main loop
        while not shutdown_requested:
            try:
                logger.debug("Waiting for motion...")
                
                # Wait for motion detection
                if pir_sensor.wait_for_motion(timeout=1.0):
                    logger.info("Motion detected! Taking photo...")
                    
                    try:
                        # Generate a filename based on timestamp
                        filename = storage.generate_filename()
                        # Use the get_photo_path method to get the full path with date directory
                        photo_path = storage.get_photo_path(filename)
                        
                        # Take a photo
                        photo_path = camera.take_photo(photo_path)
                        logger.info(f"Photo captured: {photo_path}")
                        
                        # Store photo metadata
                        metadata = {"trigger": "motion_detection"}
                        
                        # Run inference if available
                        if inference:
                            try:
                                detections = inference.detect(photo_path)
                                if detections:
                                    logger.info(f"Bird detection results: {detections}")
                                    metadata["detections"] = detections
                            except Exception as e:
                                logger.error(f"Error during inference: {e}")
                        
                        # Save metadata
                        storage.save_photo(photo_path, filename, metadata)
                        
                        # Upload if available
                        if uploader and settings.get("uploader", "auto_upload"):
                            try:
                                remote_path = os.path.basename(photo_path)
                                url = uploader.upload_photo(photo_path, remote_path)
                                logger.info(f"Photo uploaded: {url}")
                            except Exception as e:
                                logger.error(f"Error during upload: {e}")
                        
                    except Exception as e:
                        logger.exception(f"Error processing motion event: {e}")
                
                # Small sleep to prevent CPU hogging
                time.sleep(0.1)
                
            except Exception as e:
                logger.exception(f"Error in main loop iteration: {e}")
                if not shutdown_requested:
                    time.sleep(1)  # Prevent tight loop on errors
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.exception(f"Error in main loop: {e}")
    finally:
        # Clean up resources
        logger.info("Cleaning up resources")
        try:
            pir_sensor.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up PIR sensor: {e}")
        
        try:
            camera.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up camera: {e}")
        
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main() 