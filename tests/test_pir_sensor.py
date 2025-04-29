"""Tests for the PIRSensor module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import time

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sensors.pir_sensor import PIRSensor


class TestPIRSensor(unittest.TestCase):
    """Test cases for PIRSensor class."""

    @patch('src.sensors.pir_sensor.GPIO')
    def setUp(self, mock_gpio):
        """Set up test fixtures."""
        self.mock_gpio = mock_gpio
        self.pin = 17
        self.cooldown_time = 0.5
        self.sensor = PIRSensor(self.pin, self.cooldown_time)

    def test_init(self):
        """Test initialization of PIRSensor."""
        self.assertEqual(self.sensor.pin, self.pin)
        self.assertEqual(self.sensor.cooldown_time, self.cooldown_time)
        self.assertIsNotNone(self.sensor.logger)
        self.assertIsNotNone(self.sensor.last_detection_time)

    def test_setup(self):
        """Test that setup configures GPIO correctly."""
        # Setup is called in __init__, so we check if GPIO was configured correctly
        self.mock_gpio.setmode.assert_called_once_with(self.mock_gpio.BCM)
        self.mock_gpio.setup.assert_called_once_with(
            self.pin, 
            self.mock_gpio.IN, 
            pull_up_down=self.mock_gpio.PUD_DOWN
        )

    def test_detect_motion_positive(self):
        """Test motion detection when motion is detected."""
        # Mock GPIO.input to return True (motion detected)
        self.mock_gpio.input.return_value = True
        
        # Ensure cooldown doesn't interfere
        self.sensor.last_detection_time = 0
        
        result = self.sensor.detect_motion()
        
        self.mock_gpio.input.assert_called_once_with(self.pin)
        self.assertTrue(result)
        self.assertGreater(self.sensor.last_detection_time, 0)

    def test_detect_motion_negative(self):
        """Test motion detection when no motion is detected."""
        # Mock GPIO.input to return False (no motion)
        self.mock_gpio.input.return_value = False
        
        # Ensure cooldown doesn't interfere
        self.sensor.last_detection_time = 0
        
        result = self.sensor.detect_motion()
        
        self.mock_gpio.input.assert_called_once_with(self.pin)
        self.assertFalse(result)

    def test_detect_motion_cooldown(self):
        """Test that cooldown prevents repeated detections."""
        # Set last detection time to now
        self.sensor.last_detection_time = time.time()
        
        # Even if GPIO would detect motion, cooldown should prevent it
        self.mock_gpio.input.return_value = True
        
        result = self.sensor.detect_motion()
        
        # Input should not be called due to cooldown
        self.mock_gpio.input.assert_not_called()
        self.assertFalse(result)

    @patch('time.time')
    @patch('time.sleep')
    def test_wait_for_motion_success(self, mock_sleep, mock_time):
        """Test waiting for motion that is detected."""
        # Setup mock time to increment
        mock_time.side_effect = [10.0, 10.1, 10.2]
        
        # Configure detect_motion to return True on second call
        with patch.object(self.sensor, 'detect_motion', side_effect=[False, True]):
            result = self.sensor.wait_for_motion(timeout=5)
            
        self.assertTrue(result)
        # Sleep should be called once before detection
        mock_sleep.assert_called_once_with(0.1)

    @patch('time.time')
    @patch('time.sleep')
    def test_wait_for_motion_timeout(self, mock_sleep, mock_time):
        """Test waiting for motion with timeout expiring."""
        # Setup time to increment past the timeout
        mock_time.side_effect = [10.0, 10.1, 15.1]
        
        # Configure detect_motion to always return False
        with patch.object(self.sensor, 'detect_motion', return_value=False):
            result = self.sensor.wait_for_motion(timeout=5)
            
        self.assertFalse(result)
        # Sleep should be called at least once
        mock_sleep.assert_called_with(0.1)

    def test_cleanup(self):
        """Test resource cleanup."""
        self.sensor.cleanup()
        self.mock_gpio.cleanup.assert_called_once_with(self.pin)


if __name__ == '__main__':
    unittest.main() 