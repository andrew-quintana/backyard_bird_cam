#!/usr/bin/env python3
"""
Test script to verify imports on Jetson Nano.
Run this to identify which specific package or module is causing the illegal instruction error.
"""

import os
import sys
import logging
import platform
from importlib import import_module

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger('test_imports')

def system_info():
    """Print system information"""
    log.info(f"Python version: {sys.version}")
    log.info(f"Platform: {platform.platform()}")
    log.info(f"Architecture: {platform.machine()}")
    log.info(f"System: {platform.system()}")
    log.info(f"Processor: {platform.processor()}")
    
    # Check path
    log.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    log.info(f"sys.path: {sys.path}")

def test_import(module_name, submodule=None):
    """Test importing a module and handle any errors"""
    full_name = f"{module_name}.{submodule}" if submodule else module_name
    try:
        log.info(f"Trying to import {full_name}...")
        if submodule:
            base = import_module(module_name)
            module = import_module(f"{module_name}.{submodule}")
        else:
            module = import_module(module_name)
            
        version = getattr(module, '__version__', 'unknown')
        log.info(f"✓ Successfully imported {full_name} (version: {version})")
        return True
    except ImportError as e:
        log.warning(f"✗ ImportError: {e}")
        return False
    except Exception as e:
        log.error(f"✗ Error importing {full_name}: {type(e).__name__}: {e}")
        return False

def test_numerics():
    """Test numeric libraries separately with careful imports"""
    # Test numpy first as it's a dependency for others
    if test_import('numpy'):
        try:
            import numpy as np
            log.info(f"Testing basic numpy operations...")
            arr = np.array([1, 2, 3])
            result = arr.sum()
            log.info(f"✓ NumPy operations successful: {arr} -> sum={result}")
        except Exception as e:
            log.error(f"✗ NumPy operations failed: {type(e).__name__}: {e}")
    
    # Then test scikit-learn
    if test_import('sklearn'):
        try:
            from sklearn import __version__ as sklearn_version
            log.info(f"scikit-learn version: {sklearn_version}")
        except Exception as e:
            log.error(f"✗ sklearn version check failed: {type(e).__name__}: {e}")

def test_tensorflow():
    """Test TensorFlow import carefully"""
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'  # Reduce TF verbosity
    
    if test_import('tensorflow'):
        try:
            import tensorflow as tf
            log.info(f"TensorFlow version: {tf.__version__}")
            log.info(f"Keras version: {tf.keras.__version__}")
            
            # Check GPU availability
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                log.info(f"GPUs available: {len(gpus)}")
                for gpu in gpus:
                    log.info(f"  {gpu}")
            else:
                log.info("No GPUs detected by TensorFlow")
                
            # Test TensorFlow operations
            log.info("Testing basic TensorFlow operations...")
            tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            log.info(f"✓ TensorFlow operations successful: {tensor}")
            
        except Exception as e:
            log.error(f"✗ TensorFlow operations failed: {type(e).__name__}: {e}")

def test_webserver():
    """Test Flask and web components"""
    test_import('flask')
    test_import('flask_cors')
    test_import('werkzeug')

def test_image_processing():
    """Test image processing libraries"""
    if test_import('PIL'):
        try:
            from PIL import Image, __version__ as pil_version
            log.info(f"Pillow version: {pil_version}")
        except Exception as e:
            log.error(f"✗ PIL import detail failed: {type(e).__name__}: {e}")
    
    # OpenCV often causes issues on Jetson
    test_import('cv2')

def check_model_file():
    """Check if model file exists"""
    log.info("Checking for ML model file...")
    
    model_paths = [
        os.path.expanduser("~/projects/backyard_bird_cam/common/models/bird_mobilenet_v5data.keras"),
        os.path.expanduser("~/projects/backyard_bird_cam/common/models/bird_mobilenet_v5data.h5"),
        "./common/models/bird_mobilenet_v5data.keras"
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            log.info(f"✓ Model file found: {path}")
            return True
    
    log.warning("✗ Model file not found in any expected location")
    return False

if __name__ == "__main__":
    try:
        log.info("===== Testing Jetson Nano Python Package Imports =====")
        system_info()
        
        log.info("\n----- Testing Web Server Components -----")
        test_webserver()
        
        log.info("\n----- Testing Image Processing Libraries -----")
        test_image_processing()
        
        log.info("\n----- Testing Numeric and ML Libraries -----")
        test_numerics()
        
        log.info("\n----- Testing TensorFlow -----")
        test_tensorflow()
        
        log.info("\n----- Checking Model Files -----")
        check_model_file()
        
        log.info("\n===== Import Testing Complete =====")
    except Exception as e:
        log.error(f"Test script failed: {type(e).__name__}: {e}")
        sys.exit(1) 