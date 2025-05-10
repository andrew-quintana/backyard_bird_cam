"""
Compatibility layer for Jetson Nano to handle TensorFlow dependencies

This module provides safe imports and initialization for running the 
inference server on Jetson Nano hardware, handling architecture
compatibility issues gracefully.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('jetson_compatibility')

# Set environment variables to control TensorFlow behavior
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  # Reduce TensorFlow verbosity
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'  # Don't allocate all GPU memory at once

def initialize_dev_mode():
    """Initialize system for development mode without TensorFlow"""
    logger.info("Starting in Jetson-compatible development mode")
    
    # Check CPU architecture to confirm we're on ARM
    import platform
    arch = platform.machine()
    logger.info(f"Detected architecture: {arch}")
    
    if 'arm' in arch or 'aarch64' in arch:
        logger.info("Running on ARM architecture (likely Jetson)")
    else:
        logger.warning(f"Not running on expected ARM architecture: {arch}")
    
    return True
       
def safe_import_tensorflow():
    """Safely try to import TensorFlow, return None if not available"""
    try:
        logger.info("Attempting to import TensorFlow...")
        import tensorflow as tf
        logger.info(f"TensorFlow loaded successfully: {tf.__version__}")
        
        # Check TensorFlow GPU availability
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"TensorFlow detected {len(gpus)} GPU(s)")
            for gpu in gpus:
                logger.info(f"  GPU: {gpu}")
        else:
            logger.warning("No GPUs detected by TensorFlow")
            
        return tf
    except ImportError as e:
        logger.warning(f"TensorFlow import error: {e}")
        logger.info("Running in CPU-only mode without TensorFlow")
        return None
    except Exception as e:
        logger.error(f"Error initializing TensorFlow: {e}")
        logger.info("Falling back to CPU-only mode")
        return None

def get_mock_inference_engine():
    """Provide a mock inference engine when TensorFlow is unavailable"""
    logger.info("Creating mock inference engine for development")
    
    class MockInferenceEngine:
        def __init__(self):
            logger.info("MockInferenceEngine initialized")
            
        def predict(self, image):
            """Return mock prediction results"""
            import random
            birds = ["robin", "sparrow", "cardinal", "bluejay", "finch"]
            detected = random.choice([True, False])
            confidence = random.uniform(0.6, 0.95) if detected else random.uniform(0.1, 0.4)
            result = {
                "detected": detected,
                "confidence": confidence,
                "bird_type": random.choice(birds) if detected else None,
                "is_mock": True
            }
            logger.info(f"Mock inference result: {result}")
            return result
    
    return MockInferenceEngine() 