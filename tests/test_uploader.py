"""Tests for the Uploader module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.uploader.uploader import Uploader


class TestUploader(unittest.TestCase):
    """Test cases for Uploader class."""

    @patch('src.uploader.uploader.Uploader.setup')
    def setUp(self, mock_setup):
        """Set up test fixtures."""
        self.service_type = 's3'
        self.credentials = {'access_key': 'test_key', 'secret_key': 'test_secret'}
        self.uploader = Uploader(self.service_type, self.credentials)
        mock_setup.assert_called_once()

    def test_init(self):
        """Test initialization of Uploader."""
        self.assertEqual(self.uploader.service_type, self.service_type)
        self.assertEqual(self.uploader.credentials, self.credentials)

    @patch('src.uploader.uploader.Uploader.upload_photo')
    def test_upload_photo(self, mock_upload):
        """Test uploading a photo."""
        file_path = '/tmp/test_photo.jpg'
        remote_path = 'birds/test_photo.jpg'
        expected_url = 'https://bucket.s3.amazonaws.com/birds/test_photo.jpg'
        
        mock_upload.return_value = expected_url
        result = self.uploader.upload_photo(file_path, remote_path)
        
        mock_upload.assert_called_once_with(file_path, remote_path)
        self.assertEqual(result, expected_url)

    @patch('src.uploader.uploader.Uploader.list_uploaded_photos')
    def test_list_uploaded_photos(self, mock_list):
        """Test listing uploaded photos."""
        mock_photos = ['photo1.jpg', 'photo2.jpg']
        mock_list.return_value = mock_photos
        
        result = self.uploader.list_uploaded_photos()
        mock_list.assert_called_once()
        self.assertEqual(result, mock_photos)


if __name__ == '__main__':
    unittest.main() 