"""Camera handler module for taking photos."""
import os
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    from picamera2.controls import controls
except ImportError:
    # For development on non-Raspberry Pi systems
    import sys
    import types
    from PIL import Image
    import numpy as np
    
    class MockPicamera2:
        """Mock Picamera2 class for development on non-Raspberry Pi systems."""
        
        def __init__(self):
            self.logger = logging.getLogger(__name__)
            self.logger.info("Using MockPicamera2 (not running on a Raspberry Pi)")
            self.config = None
            self.camera_config = {"size": (1920, 1080)}
            self._is_configured = False
            self._is_started = False
            
        def create_still_configuration(self, main=None, **kwargs):
            """Create a still configuration."""
            return {"size": main if main else (1920, 1080)}
            
        def configure(self, config):
            """Configure the camera."""
            self.config = config
            self._is_configured = True
            
        def start(self):
            """Start the camera."""
            if not self._is_configured:
                self.configure(self.create_still_configuration())
            self._is_started = True
            
        def stop(self):
            """Stop the camera."""
            self._is_started = False
            
        def close(self):
            """Close the camera."""
            self._is_started = False
            
        def capture_file(self, filename):
            """Capture a photo to a file."""
            if not self._is_started:
                self.start()
                
            # Create a dummy image
            img = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
            
            # Add a timestamp
            from PIL import ImageDraw, ImageFont
            d = ImageDraw.Draw(img)
            text = f"Mock Camera - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            d.text((10, 10), text, fill=(255, 255, 0))
            
            # Save the image
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            img.save(filename)
            return filename
    
    # Create mock picamera2 module
    sys.modules['picamera2'] = types.ModuleType('picamera2')
    sys.modules['picamera2'].Picamera2 = MockPicamera2
    
    # Create mock encoders module
    sys.modules['picamera2.encoders'] = types.ModuleType('picamera2.encoders')
    sys.modules['picamera2.encoders'].JpegEncoder = type('JpegEncoder', (), {})
    
    # Create mock outputs module
    sys.modules['picamera2.outputs'] = types.ModuleType('picamera2.outputs')
    sys.modules['picamera2.outputs'].FileOutput = type('FileOutput', (), {'__init__': lambda self, filename: None})
    
    # Import our mocks
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput


class CameraHandler:
    """Class to handle camera operations."""

    # IMX219 camera focus range in inches
    MIN_FOCUS_DISTANCE = 8  # 20cm
    MAX_FOCUS_DISTANCE = float('inf')  # infinity

    def __init__(self, resolution=(1920, 1080), rotation=0, focus_distance_inches=24):
        """Initialize the camera with specified resolution.
        
        Args:
            resolution (tuple): Camera resolution as (width, height)
            rotation (int): Camera rotation in degrees (0, 90, 180, or 270)
            focus_distance_inches (float): Focus distance in inches (8 inches to infinity)
        """
        self.resolution = resolution
        self.rotation = rotation
        self.focus_distance_inches = focus_distance_inches
        self.camera = None
        self.logger = logging.getLogger(__name__)
        self.setup()
        
    def _convert_inches_to_lens_position(self, inches):
        """Convert distance in inches to camera lens position (0.0 to 1.0).
        
        Args:
            inches (float): Distance in inches
            
        Returns:
            float: Lens position value between 0.0 and 1.0
        """
        if inches <= self.MIN_FOCUS_DISTANCE:
            return 0.0
        elif inches == float('inf'):
            return 1.0
        else:
            # Convert using inverse relationship (closer = lower value)
            # Using a simple logarithmic scale for better distribution
            import math
            normalized = (math.log(inches) - math.log(self.MIN_FOCUS_DISTANCE)) / 10.0
            return min(max(normalized, 0.0), 1.0)
        
    def setup(self):
        """Setup the camera."""
        self.logger.info(f"Setting up camera with resolution {self.resolution}")
        
        # Initialize the camera
        self.camera = Picamera2()
        
        # Convert inches to lens position
        lens_position = self._convert_inches_to_lens_position(self.focus_distance_inches)
        
        # Create and set configuration with controls
        config = self.camera.create_still_configuration(
            main={"size": self.resolution},
            controls={
                "AfMode": controls.AfModeEnum.Manual,
                "LensPosition": lens_position,
                "AwbMode": controls.AwbModeEnum.Auto,
                "AeMode": controls.AeModeEnum.Auto,
                "AeMeteringMode": controls.AeMeteringModeEnum.Matrix,
                "AeExposureMode": controls.AeExposureModeEnum.Normal,
                "FrameDurationLimits": (33333, 33333)  # 30fps frame rate
            }
        )
        
        self.logger.debug("Available camera controls before configuration:")
        for control in self.camera.camera_controls:
            self.logger.debug(f"  {control}: {self.camera.camera_controls[control]}")
            
        self.logger.info(f"Configuring camera with controls: {config['controls']}")
        self.camera.configure(config)
        
        # Start the camera
        self.camera.start()
        
        # Allow time for auto exposure to settle
        time.sleep(0.5)
        
        self.logger.debug("Available camera controls after configuration:")
        for control in self.camera.camera_controls:
            self.logger.debug(f"  {control}: {self.camera.camera_controls[control]}")
            
        self.logger.debug("Current camera configuration:")
        self.logger.debug(f"  Streams: {self.camera.camera_configuration()}")
        self.logger.debug(f"  Properties: {self.camera.camera_properties}")
        
        # Verify the settings were applied
        current_controls = self.camera.camera_controls
        self.logger.info(f"Current camera controls: {current_controls}")
        
        self.logger.info(f"Camera configured with focus distance of {self.focus_distance_inches} inches "
                        f"(lens position: {lens_position:.2f})")
        
    def take_photo(self, output_path):
        """Take a photo and save it to the specified path.
        
        Args:
            output_path (str): Path where the photo will be saved
            
        Returns:
            str: Path to the saved photo
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        self.logger.info(f"Taking photo and saving to {output_path}")
        
        # Capture the image directly to a file
        self.camera.capture_file(output_path)
        
        self.logger.info(f"Photo saved to {output_path}")
        return output_path
    
    def take_timelapse_photos(self, output_dir, interval=5, count=10, prefix="timelapse_"):
        """Take a series of photos at regular intervals.
        
        Args:
            output_dir (str): Directory to save photos
            interval (int): Interval between photos in seconds
            count (int): Number of photos to take
            prefix (str): Prefix for photo filenames
            
        Returns:
            list: List of paths to saved photos
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Starting timelapse: {count} photos at {interval}s intervals")
        
        photo_paths = []
        for i in range(count):
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}{timestamp}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            # Take photo
            self.take_photo(output_path)
            photo_paths.append(output_path)
            
            # Wait for next interval (except after the last photo)
            if i < count - 1:
                time.sleep(interval)
                
        self.logger.info(f"Timelapse complete, {len(photo_paths)} photos taken")
        return photo_paths
        
    def cleanup(self):
        """Release camera resources."""
        if self.camera:
            self.logger.info("Cleaning up camera resources")
            self.camera.stop()
            self.camera.close()
            self.camera = None 