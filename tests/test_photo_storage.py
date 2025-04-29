"""Tests for the PhotoStorage module."""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.photo_storage import PhotoStorage


class TestPhotoStorage(unittest.TestCase):
    """Test cases for PhotoStorage class."""

    @patch('src.storage.photo_storage.PhotoStorage.setup')
    def setUp(self, mock_setup):
        """Set up test fixtures."""
        self.base_dir = 'test_photos'
        self.storage = PhotoStorage(self.base_dir)
        mock_setup.assert_called_once()

    def test_init(self):
        """Test initialization of PhotoStorage."""
        self.assertEqual(self.storage.base_dir, self.base_dir)

    @patch('os.makedirs')
    def test_setup(self, mock_makedirs):
        """Test setup creates directory."""
        # Call the real setup method
        self.storage.setup = PhotoStorage.setup.__get__(self.storage)
        self.storage.setup()
        mock_makedirs.assert_called_once_with(self.base_dir, exist_ok=True)

    @patch('src.storage.photo_storage.datetime')
    def test_generate_filename(self, mock_datetime):
        """Test filename generation."""
        # Mock the datetime to return a fixed timestamp
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20220101_120000'
        mock_datetime.datetime.now.return_value = mock_now
        
        # Set a real method for this test
        self.storage.generate_filename = PhotoStorage.generate_filename.__get__(self.storage)
        
        filename = self.storage.generate_filename()
        self.assertEqual(filename, '20220101_120000.jpg')

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.join')
    def test_save_photo(self, mock_join, mock_file):
        """Test saving photo data."""
        mock_join.return_value = os.path.join(self.base_dir, 'test.jpg')
        
        # Test with provided filename
        photo_data = b'fake_photo_data'
        filename = 'test.jpg'
        
        with patch.object(self.storage, 'generate_filename', return_value=filename):
            # Call the mocked save_photo method
            result = self.storage.save_photo(photo_data, filename)
        
        mock_file.assert_called_once_with(mock_join.return_value, 'wb')
        mock_file().write.assert_called_once_with(photo_data)
        self.assertEqual(result, mock_join.return_value)


if __name__ == '__main__':
    unittest.main() 