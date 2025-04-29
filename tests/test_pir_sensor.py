"""Tests for the PIRSensor module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sensors.pir_sensor import PIRSensor


class TestPIRSensor(unittest.TestCase):
    """Test cases for PIRSensor class."""

    @patch('src.sensors.pir_sensor.PIRSensor.setup')
    def setUp(self, mock_setup):
        """Set up test fixtures."""
        self.pin = 17
        self.sensor = PIRSensor(self.pin)
        mock_setup.assert_called_once()

    def test_init(self):
        """Test initialization of PIRSensor."""
        self.assertEqual(self.sensor.pin, self.pin)

    @patch('src.sensors.pir_sensor.PIRSensor.detect_motion')
    def test_detect_motion(self, mock_detect):
        """Test motion detection."""
        mock_detect.return_value = True
        self.assertTrue(self.sensor.detect_motion())
        
        mock_detect.return_value = False
        self.assertFalse(self.sensor.detect_motion())

    @patch('src.sensors.pir_sensor.PIRSensor.cleanup')
    def test_cleanup(self, mock_cleanup):
        """Test resource cleanup."""
        self.sensor.cleanup()
        mock_cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main() 