"""Tests for the CameraHandler module."""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import time
from datetime import datetime

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.camera.camera_handler import CameraHandler


class TestCameraHandler(unittest.TestCase):
    """Test cases for CameraHandler class."""

    @patch('src.camera.camera_handler.Picamera2')
    @patch('src.camera.camera_handler.time.sleep')
    def setUp(self, mock_sleep, mock_picamera):
        """Set up test fixtures."""
        self.mock_camera = MagicMock()
        mock_picamera.return_value = self.mock_camera
        
        self.resolution = (1920, 1080)
        self.rotation = 90
        self.camera_handler = CameraHandler(self.resolution, self.rotation)
        
        # Verify camera setup was performed correctly
        mock_picamera.assert_called_once()
        mock_sleep.assert_called_once_with(0.5)

    def test_init(self):
        """Test initialization of CameraHandler."""
        self.assertEqual(self.camera_handler.resolution, self.resolution)
        self.assertEqual(self.camera_handler.rotation, self.rotation)
        self.assertEqual(self.camera_handler.camera, self.mock_camera)
        self.assertIsNotNone(self.camera_handler.logger)

    def test_setup(self):
        """Test camera setup."""
        # Check that camera methods were called with correct arguments
        self.mock_camera.create_still_configuration.assert_called_once_with(
            main={"size": self.resolution}
        )
        self.mock_camera.configure.assert_called_once()
        self.mock_camera.start.assert_called_once()

    @patch('os.makedirs')
    def test_take_photo(self, mock_makedirs):
        """Test taking a photo."""
        output_path = '/tmp/test_photo.jpg'
        
        # Mock camera capture method
        self.mock_camera.capture_file.return_value = None
        
        # Call the method
        result = self.camera_handler.take_photo(output_path)
        
        # Check directory was created
        mock_makedirs.assert_called_once_with(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Check camera was used to capture photo
        self.mock_camera.capture_file.assert_called_once_with(output_path)
        
        # Check result
        self.assertEqual(result, output_path)

    @patch('os.makedirs')
    @patch('src.camera.camera_handler.datetime')
    def test_take_timelapse_photos(self, mock_datetime, mock_makedirs):
        """Test taking timelapse photos."""
        output_dir = '/tmp/timelapse'
        interval = 2
        count = 3
        
        # Mock timestamps for predictable filenames
        mock_now = MagicMock()
        timestamps = ['20230101_120000', '20230101_120002', '20230101_120004']
        mock_now.strftime.side_effect = timestamps
        mock_datetime.now.return_value = mock_now
        
        # Patch the take_photo method
        with patch.object(self.camera_handler, 'take_photo') as mock_take_photo:
            # Setup return values for take_photo
            expected_paths = [
                os.path.join(output_dir, f'timelapse_{ts}.jpg') for ts in timestamps
            ]
            mock_take_photo.side_effect = expected_paths
            
            # Call the method
            with patch('time.sleep') as mock_sleep:
                result = self.camera_handler.take_timelapse_photos(
                    output_dir, interval, count
                )
            
            # Verify directory creation
            mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
            
            # Verify photo taking
            self.assertEqual(mock_take_photo.call_count, count)
            
            # Verify sleep between captures (not after last photo)
            self.assertEqual(mock_sleep.call_count, count - 1)
            for call in mock_sleep.call_args_list:
                self.assertEqual(call[0][0], interval)
            
            # Verify result
            self.assertEqual(result, expected_paths)

    def test_cleanup(self):
        """Test cleanup method."""
        self.camera_handler.cleanup()
        
        self.mock_camera.stop.assert_called_once()
        self.mock_camera.close.assert_called_once()
        self.assertIsNone(self.camera_handler.camera)


if __name__ == '__main__':
    unittest.main() 