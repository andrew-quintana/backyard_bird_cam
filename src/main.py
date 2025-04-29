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


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("bird_camera.log"),
            logging.StreamHandler()
        ]
    )


def main():
    """Main function for the bird camera application."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Bird Camera application")
    
    # Initialize components
    settings = Settings()
    
    # Create 'photos' directory if it doesn't exist
    os.makedirs(settings.get("storage", "base_dir"), exist_ok=True)
    
    # Initialize components
    pir_sensor = PIRSensor(
        pin=settings.get("pir_sensor", "pin"),
        cooldown_time=settings.get("pir_sensor", "trigger_cooldown")
    )
    
    camera = CameraHandler(
        resolution=tuple(settings.get("camera", "resolution")),
        rotation=settings.get("camera", "rotation")
    )
    
    storage = PhotoStorage(
        base_dir=settings.get("storage", "base_dir"),
        max_photos=settings.get("storage", "max_photos")
    )
    
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
            logger.info("Waiting for motion...")
            
            # Wait for motion detection
            if pir_sensor.wait_for_motion(timeout=1.0):
                logger.info("Motion detected! Taking photo...")
                
                try:
                    # Generate a filename based on timestamp
                    filename = storage.generate_filename()
                    photo_path = os.path.join(storage.base_dir, filename)
                    
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
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.exception(f"Error in main loop: {e}")
    finally:
        # Clean up resources
        logger.info("Cleaning up resources")
        pir_sensor.cleanup()
        camera.cleanup()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main() 