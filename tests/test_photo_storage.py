"""Tests for the PhotoStorage module."""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.photo_storage import PhotoStorage


class TestPhotoStorage(unittest.TestCase):
    """Test cases for PhotoStorage class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = os.path.join(self.temp_dir, "test_photos")
        self.max_photos = 5
        self.storage = PhotoStorage(self.base_dir, self.max_photos)

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test initialization of PhotoStorage."""
        self.assertEqual(self.storage.base_dir, self.base_dir)
        self.assertEqual(self.storage.max_photos, self.max_photos)
        self.assertTrue(os.path.exists(self.base_dir))
        self.assertEqual(self.storage.metadata, {})

    def test_setup_creates_directory(self):
        """Test setup creates directory."""
        # Delete the directory to test creation
        shutil.rmtree(self.base_dir)
        self.assertFalse(os.path.exists(self.base_dir))
        
        # Create a new storage instance
        storage = PhotoStorage(self.base_dir)
        
        # Check directory was created
        self.assertTrue(os.path.exists(self.base_dir))

    @patch('json.load')
    def test_load_metadata(self, mock_json_load):
        """Test loading metadata."""
        # Setup mock metadata
        mock_metadata = {
            "test.jpg": {"timestamp": "2022-01-01T12:00:00", "path": "/test/path"}
        }
        mock_json_load.return_value = mock_metadata
        
        # Create metadata file
        with open(self.storage.metadata_file, 'w') as f:
            f.write("{}")  # Empty JSON object
            
        # Load metadata
        self.storage.load_metadata()
        
        # Verify json.load was called
        mock_json_load.assert_called_once()
        
        # Verify metadata was set
        self.assertEqual(self.storage.metadata, mock_metadata)
        
    @patch('json.dump')
    def test_save_metadata(self, mock_json_dump):
        """Test saving metadata."""
        # Setup metadata
        self.storage.metadata = {
            "test.jpg": {"timestamp": "2022-01-01T12:00:00", "path": "/test/path"}
        }
        
        # Mock open
        mock_file = mock_open()
        
        with patch('builtins.open', mock_file):
            self.storage.save_metadata()
            
        # Verify json.dump was called with correct arguments
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], self.storage.metadata)
        self.assertEqual(kwargs.get('indent'), 2)

    @patch('src.storage.photo_storage.datetime')
    def test_generate_filename(self, mock_datetime):
        """Test filename generation."""
        # Mock the datetime to return a fixed timestamp
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20220101_120000'
        mock_datetime.now.return_value = mock_now
        
        filename = self.storage.generate_filename()
        self.assertEqual(filename, '20220101_120000.jpg')
        
        # Test with different extension
        filename = self.storage.generate_filename(extension='.png')
        self.assertEqual(filename, '20220101_120000.png')

    @patch('src.storage.photo_storage.datetime')
    def test_save_photo_bytes(self, mock_datetime):
        """Test saving photo data as bytes."""
        # Setup mock datetime
        mock_now = MagicMock()
        mock_now.isoformat.return_value = '2022-01-01T12:00:00'
        mock_datetime.now.return_value = mock_now
        
        # Create test data
        photo_data = b'fake_photo_data'
        filename = 'test.jpg'
        
        # Save the photo
        result = self.storage.save_photo(photo_data, filename)
        
        # Verify file was saved
        full_path = os.path.join(self.base_dir, filename)
        self.assertEqual(result, full_path)
        self.assertTrue(os.path.exists(full_path))
        
        # Verify file content
        with open(full_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, photo_data)
            
        # Verify metadata
        self.assertIn(filename, self.storage.metadata)
        self.assertEqual(self.storage.metadata[filename]['filename'], filename)
        self.assertEqual(self.storage.metadata[filename]['path'], full_path)

    @patch('src.storage.photo_storage.datetime')
    def test_save_photo_file_path(self, mock_datetime):
        """Test saving photo from file path."""
        # Setup mock datetime
        mock_now = MagicMock()
        mock_now.isoformat.return_value = '2022-01-01T12:00:00'
        mock_datetime.now.return_value = mock_now
        
        # Create a test source file
        source_file = os.path.join(self.temp_dir, 'source.jpg')
        with open(source_file, 'wb') as f:
            f.write(b'source_data')
            
        # Save the photo using path
        filename = 'copied.jpg'
        result = self.storage.save_photo(source_file, filename)
        
        # Verify file was copied
        full_path = os.path.join(self.base_dir, filename)
        self.assertEqual(result, full_path)
        self.assertTrue(os.path.exists(full_path))
        
        # Verify file content
        with open(full_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'source_data')

    def test_list_photos(self):
        """Test listing photos."""
        # Create some test photos
        filenames = ['test1.jpg', 'test2.png', 'test3.jpeg', 'not_a_photo.txt']
        for filename in filenames:
            with open(os.path.join(self.base_dir, filename), 'w') as f:
                f.write('test')
                
        # Create a subdirectory (should be ignored)
        os.makedirs(os.path.join(self.base_dir, 'subdir'))
        
        # List photos
        photos = self.storage.list_photos()
        
        # Verify only image files are returned
        self.assertEqual(len(photos), 3)
        self.assertIn('test1.jpg', photos)
        self.assertIn('test2.png', photos)
        self.assertIn('test3.jpeg', photos)
        self.assertNotIn('not_a_photo.txt', photos)
        self.assertNotIn('subdir', photos)

    def test_get_photo_path(self):
        """Test getting photo path."""
        filename = 'test.jpg'
        expected_path = os.path.join(self.base_dir, filename)
        
        result = self.storage.get_photo_path(filename)
        self.assertEqual(result, expected_path)

    def test_get_photo_metadata(self):
        """Test getting photo metadata."""
        # Setup metadata
        filename = 'test.jpg'
        metadata = {'timestamp': '2022-01-01T12:00:00', 'path': '/test/path'}
        self.storage.metadata[filename] = metadata
        
        # Get metadata
        result = self.storage.get_photo_metadata(filename)
        self.assertEqual(result, metadata)
        
        # Test non-existent file
        result = self.storage.get_photo_metadata('nonexistent.jpg')
        self.assertEqual(result, {})

    def test_delete_photo(self):
        """Test deleting a photo."""
        # Create a test photo
        filename = 'test.jpg'
        full_path = os.path.join(self.base_dir, filename)
        with open(full_path, 'w') as f:
            f.write('test')
            
        # Add to metadata
        self.storage.metadata[filename] = {'timestamp': '2022-01-01T12:00:00', 'path': full_path}
        
        # Delete the photo
        result = self.storage.delete_photo(filename)
        
        # Verify photo was deleted
        self.assertTrue(result)
        self.assertFalse(os.path.exists(full_path))
        self.assertNotIn(filename, self.storage.metadata)
        
        # Test deleting non-existent photo
        result = self.storage.delete_photo('nonexistent.jpg')
        self.assertFalse(result)

    def test_enforce_max_photos(self):
        """Test enforcing maximum photos limit."""
        # Create more photos than the maximum
        num_photos = self.max_photos + 3
        filenames = [f'test{i}.jpg' for i in range(num_photos)]
        
        # Create the files with increasing timestamps
        for i, filename in enumerate(filenames):
            full_path = os.path.join(self.base_dir, filename)
            with open(full_path, 'w') as f:
                f.write('test')
            # Set creation time to simulate different creation times
            os.utime(full_path, (i, i))
            
        # Enforce max photos
        self.storage._enforce_max_photos()
        
        # Verify oldest photos were deleted
        remaining_photos = self.storage.list_photos()
        self.assertEqual(len(remaining_photos), self.max_photos)
        
        # Verify the newest photos were kept
        for i in range(num_photos - self.max_photos, num_photos):
            self.assertIn(f'test{i}.jpg', remaining_photos)
            
        # Verify the oldest photos were deleted
        for i in range(num_photos - self.max_photos):
            self.assertNotIn(f'test{i}.jpg', remaining_photos)


if __name__ == '__main__':
    unittest.main() 