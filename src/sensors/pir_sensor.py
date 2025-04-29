"""PIR Motion Sensor Module for detecting movement."""
import time
import logging
try:
    import RPi.GPIO as GPIO
except ImportError:
    # For development on non-Raspberry Pi systems
    import sys
    import types
    
    class MockGPIO:
        """Mock GPIO class for development on non-Raspberry Pi systems."""
        BCM = "BCM"
        IN = "IN"
        PUD_DOWN = "PUD_DOWN"
        
        def __init__(self):
            self.pins = {}
            self.logger = logging.getLogger(__name__)
            self.logger.info("Using MockGPIO (not running on a Raspberry Pi)")
            
        def setmode(self, mode):
            self.mode = mode
            
        def setup(self, pin, direction, pull_up_down=None):
            self.pins[pin] = False
            
        def input(self, pin):
            # Simulate random motion detection (20% chance)
            import random
            detected = random.random() < 0.2
            return detected
            
        def cleanup(self):
            self.pins = {}
    
    # Create mock GPIO module
    sys.modules['RPi'] = types.ModuleType('RPi')
    sys.modules['RPi.GPIO'] = MockGPIO()
    GPIO = sys.modules['RPi.GPIO']


class PIRSensor:
    """Class to handle PIR motion sensor operations."""

    def __init__(self, pin, cooldown_time=1.0):
        """Initialize the PIR sensor with GPIO pin.
        
        Args:
            pin (int): GPIO pin number connected to the PIR sensor
            cooldown_time (float): Time in seconds to wait between motion checks
        """
        self.pin = pin
        self.cooldown_time = cooldown_time
        self.logger = logging.getLogger(__name__)
        self.last_detection_time = 0
        self.setup()
        
    def setup(self):
        """Setup GPIO pin for PIR sensor."""
        self.logger.info(f"Setting up PIR sensor on GPIO pin {self.pin}")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def detect_motion(self):
        """Detect motion from the PIR sensor.
        
        Returns:
            bool: True if motion is detected, False otherwise
        """
        current_time = time.time()
        # Check if enough time has passed since last detection
        if current_time - self.last_detection_time < self.cooldown_time:
            return False
            
        motion_detected = GPIO.input(self.pin)
        
        if motion_detected:
            self.logger.info("Motion detected by PIR sensor")
            self.last_detection_time = current_time
            
        return motion_detected
    
    def wait_for_motion(self, timeout=None):
        """Wait for motion to be detected.
        
        Args:
            timeout (float, optional): Maximum time to wait in seconds.
                                      If None, wait indefinitely.
        
        Returns:
            bool: True if motion was detected, False if timeout occurred
        """
        self.logger.info(f"Waiting for motion (timeout: {timeout if timeout else 'none'})")
        
        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            if self.detect_motion():
                return True
            time.sleep(0.1)  # Small sleep to prevent CPU hogging
            
        self.logger.info("Timeout occurred while waiting for motion")
        return False
        
    def cleanup(self):
        """Clean up GPIO resources."""
        self.logger.info("Cleaning up PIR sensor GPIO resources")
        # Only clean up the specific pin we used
        # This is safer than GPIO.cleanup() which cleans up all pins
        GPIO.cleanup(self.pin) 