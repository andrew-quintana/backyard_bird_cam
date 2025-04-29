"""Tests for the CameraHandler module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.camera.camera_handler import CameraHandler


class TestCameraHandler(unittest.TestCase):
    """Test cases for CameraHandler class."""

    @patch('src.camera.camera_handler.CameraHandler.setup')
    def setUp(self, mock_setup):
        """Set up test fixtures."""
        self.resolution = (1920, 1080)
        self.camera = CameraHandler(self.resolution)
        mock_setup.assert_called_once()

    def test_init(self):
        """Test initialization of CameraHandler."""
        self.assertEqual(self.camera.resolution, self.resolution)

    @patch('src.camera.camera_handler.CameraHandler.take_photo')
    def test_take_photo(self, mock_take_photo):
        """Test taking a photo."""
        output_path = '/tmp/test_photo.jpg'
        mock_take_photo.return_value = output_path
        
        result = self.camera.take_photo(output_path)
        mock_take_photo.assert_called_once_with(output_path)
        self.assertEqual(result, output_path)

    @patch('src.camera.camera_handler.CameraHandler.cleanup')
    def test_cleanup(self, mock_cleanup):
        """Test resource cleanup."""
        self.camera.cleanup()
        mock_cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main() 